---
title: SPECTRE Intelligence Hub
emoji: 🕵️‍♂️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# 🕵️‍♂️ Project SPECTRE: Intelligence Hub

**Autonomous OSINT Intelligence Core & Graph Disambiguation Engine**

![SPECTRE Intelligence Core](https://img.shields.io/badge/Status-V1.2%20Stable-00f2ff?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge) ![React](https://img.shields.io/badge/React-ForceGraph-darkblue?style=for-the-badge)
[![SafeSkill 91/100](https://img.shields.io/badge/SafeSkill-91%2F100_Verified%20Safe-brightgreen)](https://safeskill.dev/scan/elvisthebuilder-spectre)

SPECTRE is a next-generation Open Source Intelligence (OSINT) gathering framework. It moves away from static terminal spreadsheets and brings reconnaissance into the future with **real-time Socket.IO graph visualizations**, **Swarm-based Deep Intelligence gathering**, and **Neural Identity Disambiguation**.

### 🌐 Model Context Protocol (MCP) Standard (Universal AI Plugin)
SPECTRE is now a **Unified Full-Stack Hub**. A single deployment hosts your high-fidelity landing page for humans and a headless MCP endpoint for AI agents.

[![Install with Smithery](https://smithery.ai/install-badge.svg)](https://smithery.ai/mcp/spectre-osint)

**🚀 One-Click Intelligence (Cloud + Local)**
The fastest way to install SPECTRE as a plugin is via Smithery. 

* **Local (Zero Setup):**
  ```bash
  npx -y @smithery/cli install spectre-osint --config GEMINI_API_KEY=your_optional_key
  ```

* **Remote (Always On):**
  Deploy SPECTRE to the cloud and point your agent to:
  `https://your-spectre-app.hf.space/mcp`

### ☁️ Deployment Guide (Hugging Face Spaces - Free)
To host SPECTRE professionally with a public URL for **FREE** (no credit card):
1. **Fork/Clone** this repository to your GitHub.
2. Go to [Hugging Face](https://huggingface.co/new-space).
3. Select **Docker SDK** and choose the **Blank** template.
4. Name your space (e.g., `spectre-hub`).
5. **Connect GitHub**: Link your repository.
6. **Add Secrets**: Go to **Settings > Variables and Secrets** and add:
   - `GEMINI_API_KEY`: Your Google GenAI key.
7. **Smithery Sync**: Once live, copy your `.hf.space` URL and paste it into [Smithery.ai/new](https://smithery.ai/new) (Remote URL: `https://.../mcp`).

**🧠 Local Intelligence Triage**
SPECTRE automatically protects your mission costs. Remote visitors see a premium landing page, while the backend tools are hidden. Full dashboard access is automatically unlocked when you run the app on `localhost`.

*Manual Integration Pattern:*
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

## 📄 License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for the full text.
