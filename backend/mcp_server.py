import os
import json
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from intelligence.engine import IntelligenceEngine

# Configure structured logging to ensure it doesn't pollute standard output
logging.basicConfig(level=logging.WARNING)

# Initialize the FastMCP Server
mcp = FastMCP("SPECTRE Core")

@mcp.tool()
async def invoke_spectre_osint(target_name: str, target_handle: str = "", target_email: str = "") -> str:
    """
    Run an autonomous SPECTRE reconnaissance mission right from your agent's context. 
    It leverages OSINT scanning (Maigret, Holehe) combined with Swarm deep research 
    to extract digital footprints and deep background intelligence on a target. 
    
    It returns a fully disambiguated JSON payload defining the primary target persona 
    vs overlapping personas.
    """
    if not target_name and not target_handle:
        return json.dumps({"error": "Target mapping failed: A name or handle is strictly required."})

    engine = IntelligenceEngine(gemini_api_key=os.getenv("GEMINI_API_KEY"))
    
    # 1. Warm up the identity swarm proxy
    payloads = {"status": "Starting MCP-OSINT Scan..."}
    try:
        await engine.swarm_manager.replenish_swarm()
        
        discovered_nodes = []
        
        # 2. Footprint OSINT (Handle)
        if target_handle:
            maigret_hits = await engine.run_maigret_recon(target_handle, "rapid")
            for res in maigret_hits:
                discovered_nodes.append({
                    "id": res["id"], "type": "SOCIAL", 
                    "label": res["site"], "url": res["url"]
                })
        
        # 3. Footprint OSINT (Email)
        if target_email:
            holehe_hits = await engine.run_holehe_recon(target_email)
            for site in holehe_hits:
                discovered_nodes.append({
                    "id": f"email_{site}", "type": "ACCOUNT", 
                    "label": f"{site} (Email)"
                })
                
        # 4. Deep Intelligence (Perplexity)
        query = (
            f"I need a deep professional and biographical background for {target_name}. "
            f"Focus on identifying their current role, notable contributions, and public digital footprint. "
            f"Link to handles or social profiles if possible."
        )
        if target_handle:
            query += f" The target also uses the handle '{target_handle}'."
        
        pplx_answer = await engine.run_perplexity_deep_search(query)
        discovered_nodes.append({
            "id": "pplx_dossier", "type": "INTEL", "description": "Continuous Intelligence Dossier"
        })
        
        # 5. Semantic Disambiguation Phase
        disambiguation = await engine.run_identity_disambiguation(
            target_name, target_handle, target_email, 
            discovered_nodes, pplx_answer
        )
        
        # 6. Format Response Object for the AI
        response_payload = {
            "target": target_name,
            "raw_deep_intel": pplx_answer,
            "disambiguated_personas": disambiguation.get("personas", []) if disambiguation else []
        }
        
        return json.dumps(response_payload, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Mission failed during execution: {str(e)}"})

if __name__ == "__main__":
    # Launch MCP Server natively linking stdio payload processing
    mcp.run(transport='stdio')
