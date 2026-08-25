# Agentic StackOverflow (Swarm IDE)

A fully self-hosted, offline coding assistant and knowledge retrieval system. The environment runs a customized micro-swarm of agents designed to write, validate, and patch local code inside a secure sandbox. It also renders a dynamic WebGL map for navigating vector databases.

## Core Capabilities

* **Self-Repairing Agent Loop (CRAG)**
When a script crashes, the system hands the stack trace to a dedicated triage trio:
- **Diagnostician (DeepSeek-R1):** Inspects the crash logs and drafts an RCA (Root Cause Analysis).
- **Coder (Qwen2.5-Coder:7b):** Drafts the patch based on the RCA.
- **Validator (Sandbox):** Executes the patch. The process recursively retries up to three times.

* **Vectorized Session Memory**
The system actively learns. Validated fixes are permanently committed to a ChromaDB memory instance. When the swarm encounters similar bugs later, it retrieves these past logs to bypass repetitive troubleshooting steps.

* **Interactive Knowledge Graph**
Browse your local document vectors visually via a 3D-force-graph WebGL overlay, featuring a custom glass-pane UI for query results.

* **Air-Gapped Execution**
Absolutely no external API calls or CDN dependencies. LLMs execute locally over Ollama, while all UI components (icons, parsers) load directly from the local static directory.

* **Heretic Mode**
Toggle the Heretic switch in the UI to dynamically re-route synthesis to an uncensored model (hermes3:8b). This drops safety constraints for unhindered logic building.

* **Audit Logging**
A built-in SQLite logger records all internal agent trajectories, token usage, and sandbox escapes. You can monitor thrashing metrics in real-time through the frontend dashboard.

## Setup Instructions

1. **Install Python Packages:**
Requires Python 3.10 or higher.
Run: pip install flask chromadb requests

2. **Pull Inference Models:**
Execute the provided script to download the required weights:
Windows: pull_models.bat
Mac/Linux: sh pull_models.sh

3. **Launch:**
Run: python 6_builder_app.py
Access the frontend at http://localhost:5000.
