<p align="center">
  <img src="https://img.shields.io/badge/Local-100%25_Offline-000000?style=for-the-badge&logo=git" alt="Offline">
  <img src="https://img.shields.io/badge/Ollama-Required-blue?style=for-the-badge&logo=ollama" alt="Ollama">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

# Swarm IDE 🐝

**An absolutely air-gapped, auto-healing developer environment.** Swarm IDE ditches cloud APIs entirely, running a customized micro-swarm of local agents over Ollama. When your code crashes, the swarm reads the stack trace, diagnoses the root cause, writes a patch, and validates it inside a local sandbox—all without human intervention.

<table>
<tr><td><b>Self-Healing CRAG Loop</b></td><td>A dedicated triage trio takes over when tests fail. DeepSeek-R1 drafts an RCA (Root Cause Analysis), Qwen2.5-Coder writes the patch, and the sandbox validates it. Retries recursively up to 3 times.</td></tr>
<tr><td><b>Autonomous Skill Creation</b></td><td>The swarm writes its own tools. Complex pipelines are saved as executable Python scripts in your workspace and dynamically loaded into the agent's context during future sessions.</td></tr>
<tr><td><b>Vectorized Memory</b></td><td>Successful bug fixes are committed permanently to a ChromaDB instance. The swarm instantly recalls these exact stack traces later, bypassing repetitive debugging.</td></tr>
<tr><td><b>Interactive 3D Graph</b></td><td>Browse your repository and vector databases visually via a gorgeous WebGL overlay, featuring a glass-pane UI for query results.</td></tr>
<tr><td><b>Heretic Mode</b></td><td>Drop the safety rails. A single toggle routes synthesis to an uncensored model (Hermes 3), completely disabling governance tracking and moralizing filters for unrestricted logic building.</td></tr>
<tr><td><b>AI Governance Dashboard</b></td><td>Monitor execution boundaries, thrashing rates, and token burn in real-time. Detailed UI drill-downs show exactly what code triggered a sandbox safety filter.</td></tr>
</table>

---

## 🧠 Architecture & How it Works

The Swarm IDE consists of three isolated layers that work in tandem to keep your code functioning without manual intervention:

1. **The Orchestrator:** Powered by \deepseek-r1:7b\. It receives your prompt and determines whether to write files, execute bash scripts, or query the RAG database.
2. **The Micro-Swarm (CRAG):** When the Orchestrator executes a script in the local sandbox and it crashes, the Micro-Swarm intervenes. It skips simple retries and instead parses the full stack trace. A specialized Coder agent (\qwen2.5-coder:7b\) applies the exact patch needed to fix the syntax or logic error.
3. **The Memory Module:** When the Micro-Swarm successfully heals a bug, it embeds the \(Crash Log + Root Cause + Patch)\ into a persistent local **ChromaDB** vector database. If the Swarm encounters this error again, it instantly retrieves the memory and solves it on the first attempt.

## 🚀 Quick Start

You need Python 3.10+ and [Ollama](https://ollama.com) installed on your machine. 

### 1. Grab the Weights
Run the included script to pull the specific local models the swarm relies on:

\\ash
# Windows
pull_models.bat

# Mac / Linux
sh pull_models.sh
\
### 2. Boot the Environment
Install the lightweight dependencies and start the local Flask server.

\\ash
pip install flask chromadb requests
python 6_builder_app.py
\
> **Note:** The UI runs on port 5000. Access your terminal at \http://localhost:5000\. No telemetry is transmitted off your machine.

---

## ⚖️ License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software in personal or commercial projects.
