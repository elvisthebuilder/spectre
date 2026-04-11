# ⚡ Project SPECTRE

**Autonomous OSINT Intelligence Core & Graph Disambiguation Engine**

![SPECTRE Intelligence Core](https://img.shields.io/badge/Status-V1.0%20Stable-00f2ff?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge) ![React](https://img.shields.io/badge/React-ForceGraph-darkblue?style=for-the-badge)

SPECTRE is a next-generation Open Source Intelligence (OSINT) gathering framework. It moves away from static terminal spreadsheets and brings reconnaissance into the future with **real-time Socket.IO graph visualizations**, **Swarm-based Deep Intelligence gathering**, and **Neural Identity Disambiguation**.

## 🧠 Why SPECTRE Exists
SPECTRE was engineered specifically to act as an **autonomous OSINT plugin for personal AI assistants (like [Jarvis](https://github.com/elvisthebuilder/jarvis))**. As AI assistants become more agentic, they require deep contextual awareness of their host. SPECTRE safely and autonomously aggregates a user’s scattered public digital footprint into a unified, disambiguated intelligence dossier. This grants an autonomous AI the capacity to deeply understand its owner for hyper-personalized interactions, proactive assistance, and contextual memory, provided the user wishes to supply that visibility.

### 🔌 API / Plugin Protocol (Agentic Integration)
To function seamlessly as a "tool" or "skill" for an external autonomous AI (like LangChain, AutoGPT, or customized assistants), SPECTRE is designed to expose its intelligence loop via a RESTful JSON bridge. Personal AIs can trigger missions asynchronously bypassing the visual frontend:
```json
// Example POST /api/v1/mission
{ "name": "Elvis Baidoo", "username": "elvisthebuilder" }
```
The FastAPI backend then returns the natively disambiguated intelligence JSON arrays directly into the AI's context window.

### 🌐 Model Context Protocol (MCP) Standard (Universal AI Plugin)
MCP is an open standard that allows any capable AI agent to natively hook into standalone tools. We provide a FastMCP server wrapper (`backend/mcp_server.py`) that acts as a universal bridge. 

Whether you are building custom AI scripts (like Jarvis), using open-source agentic IDEs (Cursor, OpenHands/Cline), or enterprise CLIs (Claude Code), you can load SPECTRE into your AI instantly. Your AI assistant will automatically discover the `@mcp.tool()` on startup, allowing it to autonomously invoke deep background OSINT scans on anyone you chat about, dynamically fetching and parsing the disambiguated JSON intelligence directly into its context window.

*Universal Integration Pattern:*
```bash
[YOUR-AI-COMMAND] mcp add spectre-osint -- python backend/mcp_server.py
```
*(Replace `[YOUR-AI-COMMAND]` with your specific assistant's CLI command, e.g., `jarvis`, `claude`, `gemini`, etc.)*

## 🚀 Key Features

*   **Real-Time Cybernetic Mapping:** Built with React and `react-force-graph`, SPECTRE maps a target's digital footprint (social handles, emails) natively as nodes and edges in a cyberpunk-themed 2D interface as soon as the backend intercepts them.
*   **Swarm Intelligence Routing (Perplexity Evasion):** Automated headless session booting (Playwright/Emailnator) dynamically spins up disposable identities on the fly, allowing the engine to pull localized deep-research dossiers from Perplexity AI without getting rate-limited or blocked.
*   **Neural Disambiguation (Gemini 2.0 Flash):** Contaminated data is a thing of the past. Once a mission concludes, SPECTRE feeds the entire mapping node array and deep dossier to an LLM. It parses semantic overlaps to isolate conflicting footprint data (e.g. tracking down "Elvis" the developer vs. "Elvis" the musician) and magically slices the graph topology to group data intelligently.

## ⚙️ Architecture

*   **Backend:** FastAPI (Async/Uvicorn), Socket.IO, Maigret, Google GenAI
*   **Frontend:** Vite, React, Lucide Icons, ReactMarkdown
*   **Automation:** Patchright (Playwright anti-detect browser for session handling)

## 🛠️ Setup & Installation

**1. Clone & Core Setup**
```bash
git clone https://github.com/yourusername/spectre-osint.git
cd spectre
```

**2. Backend Initialization**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

**3. Configure Environment**
Create a `.env` in the `backend` directory:
```env
GEMINI_API_KEY="your_google_gemini_api_key"
```

**4. Frontend Initialization**
```bash
cd frontend
pnpm install
```

**5. Launch Mission Control**
```bash
chmod +x run_spectre.sh
./run_spectre.sh
```

## 🙏 Acknowledgments & Credits

To prevent copyright infringement and adhere to open-source licenses, Project SPECTRE proudly acknowledges the following third-party services and repositories that make this architecture possible:

*   **[helallao/perplexity-ai](https://github.com/helallao/perplexity-ai)**: The unofficial Python client architecture used to model our programmatic interactions with Perplexity AI (via MIT License).
*   **[Emailnator](https://www.emailnator.com/)**: The temporary disposable email service utilized by our swarm to generate rotating identities for unbiased research capabilities.
*   **[Maigret](https://github.com/soxoj/maigret)**: Powered by Soxoj, utilized for our high-speed global digital footprint username reconnaissance.
*   **[Holehe](https://github.com/megadose/holehe)**: Utilized to efficiently reverse-search compromised and registered email footprints.

## ⚠️ Disclaimer
Project SPECTRE is an OSINT security tool developed strictly for defensive analysis, digital footprint research, and educational purposes. Ensure you have authorization when mapping technical targets.

## 🤝 Contributing
SPECTRE V1 is active! Pull requests for adding new Intelligence Nodes, scaling the UI, or increasing Swarm redundancy are welcome.
