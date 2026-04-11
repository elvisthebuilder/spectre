import asyncio
import json
import os
import logging
from typing import List, Optional
from perplexity.client import Client as PerplexityClient

logger = logging.getLogger("Spectre-Swarm")

class SwarmManager:
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.identities_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "identities.json")
        self.emailnator_cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "emailnator_cookies.json")
        self.pool: List[PerplexityClient] = []
        self._current_idx = 0
        self._lock = asyncio.Lock()
        
        # Load existing pool
        self._load_pool()

    def _load_pool(self):
        """Loads available identities from identities.json."""
        if os.path.exists(self.identities_path):
            try:
                with open(self.identities_path, "r") as f:
                    data = json.load(f)
                    for cookie_dict in data:
                        client = PerplexityClient(cookies=cookie_dict)
                        # We don't verify quota here to keep it fast; 
                        # engine will handle exhausted accounts
                        self.pool.append(client)
                logger.info(f"Loaded {len(self.pool)} identities into the swarm.")
            except Exception as e:
                logger.error(f"Failed to load identity pool: {e}")

    def _save_pool(self):
        """Saves current pool cookies to identities.json."""
        try:
            cookie_data = [client.session.cookies.get_dict() for client in self.pool]
            with open(self.identities_path, "w") as f:
                json.dump(cookie_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save identity pool: {e}")

    async def get_client(self) -> PerplexityClient:
        """Returns the next available client from the pool (Round-Robin). Waits if empty."""
        wait_cycles = 0
        while not self.pool:
            if wait_cycles > 15:
                raise Exception("Swarm generation blocked/timeout.")
            logger.info("Swarm is currently empty. Waiting for identity generation...")
            await asyncio.sleep(2)
            wait_cycles += 1
            
        async with self._lock:
            client = self.pool[self._current_idx]
            self._current_idx = (self._current_idx + 1) % len(self.pool)
            return client

    async def replenish_swarm(self):
        """Background task to fill the pool up to pool_size."""
        if len(self.pool) >= self.pool_size:
            return

        if not os.path.exists(self.emailnator_cookies_path):
            logger.error("Cannot replenish swarm: missing emailnator_cookies.json")
            return

        try:
            with open(self.emailnator_cookies_path, "r") as f:
                emailnator_cookies = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Emailnator cookies for swarm: {e}")
            return

        logger.info(f"Swarm replenishment started. Goal: {self.pool_size} (Current: {len(self.pool)})")
        
        while len(self.pool) < self.pool_size:
            try:
                # Create a new account in a thread to not block the event loop
                new_client = PerplexityClient()
                await asyncio.to_thread(new_client.create_account, emailnator_cookies)
                
                async with self._lock:
                    self.pool.append(new_client)
                    self._save_pool()
                
                logger.info(f"Swarm replenished: {len(self.pool)}/{self.pool_size}")
                # Rate limit replenishment to avoid being flagged
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Failed to generate swarm identity: {e}")
                await asyncio.sleep(10) # Wait before retrying instead of breaking

    async def remove_exhausted(self, client: PerplexityClient):
        """Removes a client from the pool if it has no Pro queries remaining."""
        async with self._lock:
            if client in self.pool:
                self.pool.remove(client)
                self._save_pool()
                logger.info("Exhausted identity removed from swarm.")
                # Trigger replenishment
                asyncio.create_task(self.replenish_swarm())
