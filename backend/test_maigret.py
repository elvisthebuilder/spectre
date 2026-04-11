"""
SPECTRE Component Test: Maigret OSINT Engine
Run: .venv/bin/python test_maigret.py <username>
"""
import asyncio
import sys
import os
import logging
import json

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("SPECTRE-TEST")

from maigret.checking import maigret as maigret_search
from maigret.result import MaigretCheckStatus
from maigret.sites import MaigretDatabase
import maigret

async def test_maigret(username: str):
    logger.info(f"=== Testing Maigret for username: '{username}' ===")
    
    # Load DB
    db = MaigretDatabase()
    maigret_dir = os.path.dirname(maigret.__file__)
    db_path = os.path.join(maigret_dir, "resources", "data.json")
    db.load_from_path(db_path)

    top_sites = ["GitHub", "Twitter", "Instagram", "Reddit", "Medium", "Facebook", "YouTube", "TikTok"]
    sites = [s for s in db.sites_dict.values() if s.name in top_sites]
    
    logger.info(f"Sites loaded for scan: {[s.name for s in sites]}")
    site_dict = {s.name: s for s in sites}
    
    # Run search
    all_results = await maigret_search(
        username=username,
        site_dict=site_dict,
        logger=logger,
        timeout=10,
    )
    
    print("\n=== RAW RESULTS DUMP ===")
    claimed = []
    for sitename, res_wrapper in all_results.items():
        status_obj = res_wrapper.get('status') if isinstance(res_wrapper, dict) else res_wrapper
        status_val = getattr(status_obj, 'status', None)
        url = getattr(status_obj, 'site_url_user', None)
        print(f"  [{sitename}] status={status_val} | url={url} | wrapper_type={type(res_wrapper).__name__}")
        
        if status_obj and status_val == MaigretCheckStatus.CLAIMED:
            claimed.append({"site": sitename, "url": url})

    print(f"\n=== CLAIMED PROFILES ({len(claimed)}) ===")
    for r in claimed:
        print(f"  ✓ {r['site']}: {r['url']}")

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "elvisthebuilder"
    asyncio.run(test_maigret(username))
