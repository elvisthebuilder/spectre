import asyncio
import logging
from typing import List, Dict, Any, Optional
from perplexity.client import Client as PerplexityClient
from maigret.checking import maigret as maigret_search
from maigret.result import MaigretCheckStatus
from maigret.sites import MaigretDatabase
from holehe import core as holehe_core
import os
from google import genai
from google.genai import types as genai_types
import maigret
import json
from intelligence.swarm_manager import SwarmManager

logger = logging.getLogger("Spectre-Engine")

class IntelligenceEngine:
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        self.gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
        self.swarm_manager = SwarmManager(pool_size=10)
        # NOTE: replenish_swarm() must be scheduled from an async context (main.py)
        
        # Load Emailnator cookies for account rotation
        self.emailnator_cookies = {}
        try:
            cookie_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "emailnator_cookies.json")
            if os.path.exists(cookie_path):
                with open(cookie_path, "r") as f:
                    self.emailnator_cookies = json.load(f)
                    logger.info("Found bootstrapped Emailnator session.")
        except Exception as e:
            logger.warning(f"Could not load Emailnator cookies: {e}")

        # Load Maigret database from internal resources
        self.maigret_db = MaigretDatabase()
        maigret_dir = os.path.dirname(maigret.__file__)
        db_path = os.path.join(maigret_dir, "resources", "data.json")
        self.maigret_db.load_from_path(db_path)

    async def ensure_perplexity_pro(self):
        """DEPRECATED: Now handled by SwarmManager automatically."""
        return True
        
    async def run_maigret_recon(self, username: str, scan_depth: str = "rapid") -> List[Dict[str, str]]:
        """Perform technical handle reconnaissance."""
        if not username:
            return []
            
        logger.info(f"Running Maigret for handle: {username}")
        
        # Select sites based on depth
        if scan_depth == "deep":
            sites = list(self.maigret_db.sites_dict.values())
        else:
            top_sites = ["GitHub", "Twitter", "Instagram", "Reddit", "Medium", "Facebook", "YouTube", "TikTok"]
            sites = [s for s in self.maigret_db.sites_dict.values() if s.name in top_sites]
            if not sites:
                # Fallback to top sites by rank if specific list failed
                sites = self.maigret_db.ranked_sites_dict(top=100).values()

        site_dict = {s.name: s for s in sites}
        
        all_results = await maigret_search(
            username=username,
            site_dict=site_dict,
            logger=logger,
            timeout=5,
        )

        results = []
        for sitename, res_wrapper in all_results.items():
            check_result = res_wrapper.get('status') if isinstance(res_wrapper, dict) else res_wrapper
            if not check_result:
                continue
            
            url = getattr(check_result, 'site_url_user', None)
            status = getattr(check_result, 'status', None)
            
            # Skip truly negative results (no URL, or explicitly "not found" via Illegal)
            if not url or status == MaigretCheckStatus.ILLEGAL:
                continue

            # Assign confidence by status
            if status == MaigretCheckStatus.CLAIMED:
                confidence = 1.0
                verified = True
            elif status == MaigretCheckStatus.UNKNOWN:
                confidence = 0.6
                verified = False  # bot-blocked, inconclusive
            else:  # Available — likely bot-blocked false negative
                confidence = 0.5
                verified = False

            results.append({
                "id": f"maigret_{sitename}",
                "site": sitename,
                "url": url,
                "type": "SOCIAL",
                "confidence": confidence,
                "verified": verified,
            })
        return results

    async def run_holehe_recon(self, email: str) -> List[str]:
        """Perform email footprint analysis."""
        if not email:
            return []
            
        logger.info(f"Running Holehe for email: {email}")
        out = []
        modules = holehe_core.import_submodules("holehe.modules")
        
        # Run holehe modules in parallel
        # Note: holehe is partially sync, using to_thread
        tasks = [asyncio.to_thread(module.main, email, out) for module in modules]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return [res["name"] for res in out if res["exists"]]

    async def run_perplexity_deep_search(self, query: str) -> str:
        """Perform deep context research using the Identity Swarm."""
        logger.info(f"Running Swarm Research: {query}")
        
        try:
            # Get next identity from the swarm (will raise Exception if it times out)
            client = await self.swarm_manager.get_client()
            
            # Note: The unofficial client is synchronous
            response = await asyncio.to_thread(
                client.search, 
                query, 
                mode="deep research"
            )
            
            # Check if this search exhausted the account
            if client.copilot <= 0:
                await self.swarm_manager.remove_exhausted(client)
                
            return response.get("answer", "No research data located.")
        except Exception as e:
            logger.error(f"Swarm search failed: {e}. Executing Gemini fallback...")
            return await self.run_gemini_fallback_research(query)

    async def run_gemini_fallback_research(self, query: str) -> str:
        """High-fidelity fallback using Gemini 2.0 Flash when Perplexity is unavailable."""
        if not self.gemini_client:
            return "Mission compromised: No research fallback available (Gemini API Key missing)."
            
        prompt = (
            f"You are the SPECTRE Intelligence Core. Your Perplexity search bridge is currently offline. "
            f"Use your internal training data to perform a deep professional and biographical deep-dive for this query: '{query}'.\n\n"
            f"Provide a structured, high-confidence reconnaissance report identifying the target's probable identity, "
            f"professional achievements, and known digital footprint. Do not mention that you are an AI; speak as the mission core."
        )
        
        try:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Emergency mission abort: Fallback research failed: {str(e)}"

    async def run_identity_disambiguation(self, target_name: str, target_handle: str, target_email: str, nodes: list, dossier_text: str):
        """Cross-references all OSINT nodes against the Deep Intel dossier to decouple alternative personas."""
        if not self.gemini_client:
            return None
            
        nodes_summary = json.dumps([{"id": n["id"], "label": n["label"], "url": n.get("url")} for n in nodes])
        
        prompt = (
            f"You are the SPECTRE Intelligence Core. Disambiguate the following intelligence for target '{target_name}' "
            f"(Known handle: {target_handle}, Known email: {target_email}).\n\n"
            f"OSINT Nodes Found:\n{nodes_summary}\n\n"
            f"Deep Intelligence Dossier:\n{dossier_text}\n\n"
            f"Determine which OSINT Nodes and the Deep Intelligence Dossier ('pplx_dossier') belong to the intended developer target, "
            f"and which belong to an alternative persona with the same name (if any). "
            f"Return ONLY valid JSON in this exact structure, with no markdown formatting:\n"
            '{"personas": [{"id": "root_user", "label": "Target Persona", "owned_node_ids": ["email_...", "pplx_dossier", ...], "reason": "..."}, {"id": "alt_persona_1", "label": "Alternative Persona", "owned_node_ids": ["social_...", ...], "reason": "..."}]}'
        )
        
        try:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            # Clean possible markdown formatting
            raw_json = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(raw_json)
        except Exception as e:
            logger.error(f"Disambiguation failed: {e}")
            return None

    async def perform_confidence_match(self, bio_a: str, bio_b: str) -> float:
        """Use Gemini to compare two biographies and return a confidence score (0-1.0)."""
        if not self.gemini_client:
            return 0.5 # Neutral fallback
            
        prompt = (
            f"Compare these two digital biographies/descriptions and determine if they describe the same person.\n"
            f"Profile A: {bio_a}\n"
            f"Profile B: {bio_b}\n\n"
            f"Respond ONLY with a decimal probability between 0.0 and 1.0."
        )
        try:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return float(response.text.strip())
        except:
            return 0.5

    async def run_spectral_synthesis(self, name: str, handle: str, email: str, scan_depth: str = "rapid"):
        """Orchestrate the full reconnaissance mission with Gemini synthesis."""
        # Top-level orchestration handled by main.py WebSockets for real-time streaming
        pass
