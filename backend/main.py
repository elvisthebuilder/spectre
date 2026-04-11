import logging
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import socketio
import asyncio
from intelligence.engine import IntelligenceEngine

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Spectre-Backend")

app = FastAPI(title="Project Spectre AI Intelligence Engine")

# CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO for Real-time Graph Interaction
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio, app)

@app.get("/")
async def root():
    return {"status": "Spectre Intelligence Core Online", "version": "0.1.0-Spectral"}

@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    await sio.emit("system_status", {"message": "Neural Handshake Established, Sir."}, to=sid)

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@sio.event
async def initiate_mission(sid, data):
    """Start a new reconnaissance mission."""
    target_name = data.get("name")
    target_handle = data.get("handle")
    target_email = data.get("email")
    scan_type = data.get("scanType", "rapid")
    
    logger.info(f"Initiating mission for: {target_name} ({target_handle})")
    
    # Send initial node
    await sio.emit("discovery_event", {
        "type": "NODE_FOUND",
        "data": {
            "id": "root_user",
            "type": "USER",
            "label": target_name or target_handle,
            "description": "Primary Intelligence Target"
        }
    }, to=sid)
    
    # Placeholder for mission logic
    engine = IntelligenceEngine(gemini_api_key=os.getenv("GEMINI_API_KEY"))
    # Start swarm replenishment in the live async event loop
    asyncio.create_task(engine.swarm_manager.replenish_swarm())
    asyncio.create_task(run_mission_logic(sid, engine, target_name, target_handle, target_email, scan_type))

async def run_mission_logic(sid, engine, name, handle, email, scan_type):
    """Actual reconnaissance orchestration."""
    discovered_nodes = []
    # 1. Technical Footprint (Username)
    if handle:
        await sio.emit("discovery_event", {"type": "STATUS_UPDATE", "data": "Initiating handle reconnaissance..."}, to=sid)
        maigret_results = await engine.run_maigret_recon(handle, scan_type)
        for res in maigret_results:
            node_data = {
                "id": res["id"],
                "type": "SOCIAL",
                "label": res["site"],
                "url": res["url"],
                "description": f"Handle '{handle}' located on {res['site']}."
            }
            discovered_nodes.append(node_data)
            await sio.emit("discovery_event", {
                "type": "NODE_FOUND",
                "data": node_data
            }, to=sid)
            await sio.emit("discovery_event", {
                "type": "LINK_FOUND",
                "data": { "source": "root_user", "target": res["id"], "confidence": 1.0 }
            }, to=sid)
            await asyncio.sleep(0.5)

    # 2. Email Footprint
    if email:
        await sio.emit("discovery_event", {"type": "STATUS_UPDATE", "data": "Mapping email footprint..."}, to=sid)
        holehe_results = await engine.run_holehe_recon(email)
        for site in holehe_results:
            node_id = f"email_{site}"
            node_data = {
                "id": node_id,
                "type": "ACCOUNT",
                "label": f"{site} (Email)",
                "description": f"Verified registration for '{email}' on {site}."
            }
            discovered_nodes.append(node_data)
            await sio.emit("discovery_event", {
                "type": "NODE_FOUND",
                "data": node_data
            }, to=sid)
            await sio.emit("discovery_event", {
                "type": "LINK_FOUND",
                "data": { "source": "root_user", "target": node_id, "confidence": 1.0 }
            }, to=sid)
            await asyncio.sleep(0.5)

    # 3. Deep Research (Perplexity)
    if name:
        query = (
            f"I need a deep professional and biographical background for {name}. "
            f"Focus on identifying their current role, notable contributions, and public digital footprint. "
            f"Link to handles or social profiles if possible."
        )
        if handle:
            query += f" The target also uses the handle '{handle}'."
        if email:
            query += f" The target's associated email is '{email}'."

        await sio.emit("discovery_event", {"type": "STATUS_UPDATE", "data": "Synthesizing deep research dossier..."}, to=sid)
        pplx_answer = await engine.run_perplexity_deep_search(query)
        
        node_data = {
            "id": "pplx_dossier",
            "type": "INTEL",
            "label": "Deep Intel",
            "description": "Comprehensive Intelligence Dossier"
        }
        discovered_nodes.append(node_data)
        
        await sio.emit("discovery_event", {
            "type": "NODE_FOUND",
            "data": node_data
        }, to=sid)
        await sio.emit("discovery_event", {
            "type": "LINK_FOUND",
            "data": { "source": "root_user", "target": "pplx_dossier", "confidence": 0.9 }
        }, to=sid)
        
        # Send full dossier content separately for the Node Inspector
        await sio.emit("discovery_event", {
            "type": "INTEL_REPORT",
            "data": {
                "node_id": "pplx_dossier",
                "content": pplx_answer
            }
        }, to=sid)

        # 4. Neural Disambiguation Phase
        await sio.emit("discovery_event", {"type": "STATUS_UPDATE", "data": "Initiating Deep Neural Disambiguation..."}, to=sid)
        disambiguation = await engine.run_identity_disambiguation(name, handle, email, discovered_nodes, pplx_answer)
        if disambiguation and "personas" in disambiguation:
            for persona in disambiguation["personas"]:
                if persona["id"] != "root_user" and len(persona.get("owned_node_ids", [])) > 0:
                    # Create the new user node
                    await sio.emit("discovery_event", {
                        "type": "NODE_FOUND",
                        "data": {
                            "id": persona["id"],
                            "type": "USER",
                            "label": persona.get("label", "Unknown Alias"),
                            "description": f"Disambiguated Alternate Persona: {persona.get('reason', '')}",
                            "confidence": 0.5
                        }
                    }, to=sid)
                    
                    # Re-assign nodes
                    for nid in persona.get("owned_node_ids", []):
                        await sio.emit("discovery_event", {
                            "type": "LINK_REMOVE",
                            "data": { "source": "root_user", "target": nid }
                        }, to=sid)
                        await sio.emit("discovery_event", {
                            "type": "LINK_FOUND",
                            "data": { "source": persona["id"], "target": nid, "confidence": 0.8 }
                        }, to=sid)
                        await asyncio.sleep(0.2)
                    
                    # Send reason
                    if "reason" in persona:
                         await sio.emit("discovery_event", {"type": "STATUS_UPDATE", "data": f"AI Filter: {persona['reason']}"}, to=sid)

    await sio.emit("discovery_event", {"type": "STATUS_UPDATE", "data": "MISSION COMPLETE: SPECTRE STABILIZED."}, to=sid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(sio_app, host="0.0.0.0", port=8000)
