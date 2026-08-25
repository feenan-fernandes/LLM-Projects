# Swarm IDE (Agentic StackOverflow)

A 100% local, autonomous AI coding agent and RAG-powered knowledge base. Swarm IDE features a true **Multi-Agent Micro-Swarm** that autonomously writes, tests, and heals code in a local sandbox, combined with an interactive 3D WebGL knowledge graph.

## Key Features

* **Multi-Agent Self-Healing Swarm (CRAG)**
When code fails in the sandbox, a dedicated 3-part micro-swarm takes over:
- **Diagnostician (DeepSeek-R1):** Analyzes the stack trace and formulates a Root Cause Analysis (RCA).
- **Coder (Qwen2.5-Coder:7b):** Writes the precise, corrected Python implementation.
- **Validator (Sandbox):** Runs the fix. Loops up to 3 times automatically.

* **Episodic Swarm Memory**
The Swarm learns. Successful bug fixes are embedded into a ChromaDB memory collection. Future errors trigger a memory recall, instantly injecting Past Learnings into the Diagnostician's prompt to solve known issues on the first attempt.

* **Living RAG & 3D Knowledge Map**
Navigate vector knowledge visually through a dynamic WebGL interface. Search results are presented in a sleek glassmorphism UI overlying the network.

* **100% Air-Gapped & Offline**
Zero reliance on external APIs or CDNs. All LLM inference runs locally via Ollama. All UI assets are served locally via Flask.

* **Heretic (Uncensored) Mode**
Toggle Heretic Mode in the UI to dynamically swap the Orchestrator to an uncensored model (hermes3:8b), bypassing alignment filters for unrestricted logic generation and RAG synthesis.

* **AI Governance & Auditing**
Comprehensive SQLite logging tracks every agent thought, tool execution, and sandbox boundary violation. View real-time token burn and thrashing rates directly in the UI dashboard.

## Installation & Setup

1. **Install Requirements:**
Ensure you have Python 3.10+ installed.
Run: pip install flask chromadb requests

2. **Install Local LLMs:**
Run the included setup script to pull the required local models:
Windows: pull_models.bat
Mac/Linux: sh pull_models.sh

3. **Run the Server:**
Run: python 6_builder_app.py
Navigate to http://localhost:5000 in your browser.