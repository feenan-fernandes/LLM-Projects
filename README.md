<p align="center">
  <img src="https://img.shields.io/badge/Local-100%25_Offline-000000?style=for-the-badge&logo=git" alt="Offline">
  <img src="https://img.shields.io/badge/Ollama-Required-blue?style=for-the-badge&logo=ollama" alt="Ollama">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge&logo=python" alt="Python">
</p>

# Swarm IDE 🐝

**An absolutely air-gapped, auto-healing developer environment.** Swarm IDE ditches cloud APIs entirely, running a customized micro-swarm of local agents over Ollama. When your code crashes, the swarm reads the stack trace, diagnoses the root cause, writes a patch, and validates it inside a local sandbox—all without human intervention.

<table>
<tr><td><b>Self-Healing CRAG Loop</b></td><td>A dedicated triage trio takes over when tests fail. DeepSeek-R1 drafts an RCA, Qwen2.5-Coder writes the patch, and the sandbox validates it. Retries recursively.</td></tr>
<tr><td><b>Autonomous Skill Creation</b></td><td>The swarm writes its own tools. Complex pipelines are saved as executable Python scripts in your workspace and dynamically loaded into the agent's context during future sessions.</td></tr>
<tr><td><b>Vectorized Memory</b></td><td>Successful bug fixes are committed permanently to a ChromaDB instance. The swarm instantly recalls these exact stack traces later, bypassing repetitive debugging.</td></tr>
<tr><td><b>Interactive 3D Graph</b></td><td>Browse your repository and vector databases visually via a gorgeous WebGL overlay, featuring a glass-pane UI for query results.</td></tr>
<tr><td><b>Heretic Mode</b></td><td>Drop the safety rails. A single toggle routes synthesis to an uncensored model (Hermes 3), completely disabling governance tracking and moralizing filters for unrestricted logic building.</td></tr>
</table>

---

## Quick Start

You need Python 3.10+ and [Ollama](https://ollama.com) installed on your machine. 

### 1. Grab the Weights
Run the included batch/shell script to pull the specific local models the swarm relies on:

`ash
# Windows
pull_models.bat

# Mac / Linux
sh pull_models.sh
`

### 2. Boot the Environment
Install the lightweight dependencies and start the local Flask server.

`ash
pip install flask chromadb requests
python 6_builder_app.py
`

> **Note:** The UI runs on port 5000. Access your terminal at http://localhost:5000. No telemetry is transmitted off your machine.