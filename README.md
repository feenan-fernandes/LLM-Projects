<div align="left">
  <a href="./README.md" style="padding: 10px; border-bottom: 2px solid #58a6ff; text-decoration: none; color: #c9d1d9; font-weight: bold;">?? README</a>
  &nbsp;&nbsp;&nbsp;
  <a href="./SUPPORT.md" style="padding: 10px; border-bottom: 2px solid transparent; text-decoration: none; color: #8b949e; font-weight: bold;">?? SUPPORT / GUIDE</a>
</div>
<br>
<p align="center">
  <img src="https://img.shields.io/badge/Local-100%25_Offline-000000?style=for-the-badge&logo=git" alt="Offline">
  <img src="https://img.shields.io/badge/Ollama-Required-blue?style=for-the-badge&logo=ollama" alt="Ollama">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

# Swarm IDE

**An absolutely air-gapped, auto-healing developer environment.** Swarm IDE ditches cloud APIs entirely, running a customized micro-swarm of local agents over Ollama. When your code crashes, the swarm reads the stack trace, diagnoses the root cause, writes a patch, and validates it inside a local sandbox - all without human intervention.

## ?? System Architecture

The Swarm IDE consists of highly specialized, decoupled layers that work in tandem to keep your code functioning without manual intervention:

1. **The Orchestrator (Dynamic Routing):** The primary agent interface. You can dynamically switch models on the fly (e.g., Qwen2.5-Coder, DeepSeek-R1, Hermes-3) via the UI. It receives your prompt and determines whether to write files, search the web, execute bash scripts, or query the RAG database.
2. **The Micro-Swarm (CRAG):** When the Orchestrator executes a script in the local sandbox and it crashes, the Micro-Swarm intervenes. It skips simple retries and instead parses the full stack trace. A specialized Coder agent applies the exact patch needed to fix the syntax or logic error. Parallel sub-agents seamlessly inherit your selected model to prevent VRAM deadlock.
3. **The Memory Module:** When the Micro-Swarm successfully heals a bug, it embeds the (Crash Log + Root Cause + Patch) into a persistent local **ChromaDB** vector database. If the Swarm encounters this error again, it instantly retrieves the memory and solves it on the first attempt.
4. **Hardened Backend Deployment:** The server utilizes a production-ready **Waitress** WSGI deployment safely bound to 127.0.0.1. It features strict DoS thread locking to prevent Local LLM Memory Exhaustion (OOM) by locking the autonomous agent loop to a single concurrent background task.

## ? Core Capabilities

<table>
<tr><td><b>71+ Design Skill Contracts</b></td><td>The Swarm is pre-loaded with over 71 specialized UI/UX design frameworks natively integrated into the workspace (including <i>Taste Skill</i>, <i>Impeccable</i>, <i>Shadcn</i>, <i>Bento</i>, and the full <i>Awesome Design</i> library). The AI automatically enforces these design constraints to prevent generic, templated UI generation.</td></tr>
<tr><td><b>Agentic Web Research</b></td><td>Integrated <code>duckduckgo-search</code>. Without needing a paid API key, your offline models can autonomously crawl the live internet to read documentation and fetch framework updates before writing code.</td></tr>
<tr><td><b>AST Auto-Linting</b></td><td>Intercepts files using Python's native <code>py_compile</code> before they hit the execution sandbox. Instantly feeds syntax errors back to the agent for real-time Self-Healing without wasting Docker iterations.</td></tr>
<tr><td><b>Content & Watermark Scrubbing</b></td><td>Natively includes deterministic tools (<code>remove-ai-marks</code> and <code>clean-user-facing-text</code>) to automatically strip C2PA/AI provenance marks, invisible Unicode, and humanize generated text.</td></tr>
<tr><td><b>Heretic Mode</b></td><td>Drop the safety rails. A single toggle routes synthesis to an uncensored model (Hermes 3), completely disabling moralizing filters for unrestricted logic building.</td></tr>
<tr><td><b>AI Governance Dashboard</b></td><td>Monitor execution boundaries, thrashing rates, and token burn in real-time. Includes a built-in SQLite dashboard to track total autonomous actions and Heretic Mode invocations.</td></tr>
</table>

## ?? Quick Start

You need Python 3.10+ and [Ollama](https://ollama.com) installed on your machine. 

### 1. Grab the Weights
Run the included script to pull the specific local models the swarm relies on:

`ash
# Windows
pull_models.bat

# Mac / Linux
sh pull_models.sh
`

### 2. Install Dependencies
`ash
pip install flask chromadb requests waitress duckduckgo-search pandas
`

### 3. Boot the Environment (One-Click)
For Windows users, simply double-click the **Start-Swarm.bat** file (or the **Swarm IDE** desktop shortcut). 
This will automatically start the Ollama daemon, boot the Python backend, and open your web browser to http://127.0.0.1:5000.

Alternatively, start it manually:
`ash
ollama serve
python 6_builder_app.py
`

---

## License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software in personal or commercial projects.
