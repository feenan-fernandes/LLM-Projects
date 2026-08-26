<div align="left">
  <a href="./README.md" style="padding: 10px; border-bottom: 2px solid transparent; text-decoration: none; color: #8b949e; font-weight: bold;">📖 README</a>
  &nbsp;&nbsp;&nbsp;
  <a href="./SUPPORT.md" style="padding: 10px; border-bottom: 2px solid #58a6ff; text-decoration: none; color: #c9d1d9; font-weight: bold;">📘 SUPPORT / GUIDE</a>
</div>
<br>
# Swarm IDE - Complete User Guide

Welcome to **Swarm IDE**, a privacy-first, fully local autonomous AI software engineering environment. This guide explains how to use the IDE's core features, manage agentic tasks, and customize the underlying AI models.

---

## 1. Getting Started

### Launching the IDE
To start the Swarm IDE, simply run the main Python script from the root of the project:
`bash
python 6_builder_app.py
`
By default, the server will host the UI at http://127.0.0.1:5000. Navigate to this URL in your browser.

---

## 2. Modes of Operation

The IDE operates in distinct modes, dynamically adjusting its routing based on your request:

### A. The "Search" Mode (Agentic RAG)
Located in the **Search** tab, this is for knowledge retrieval against your codebase. 
- You can ask questions about your existing code, architecture, or how to implement a specific pattern.
- The system uses ChromaDB to perform semantic search, validates the retrieved context using a lightweight evaluation agent (Librarian), and generates a synthesized answer.

### B. The "Builder" Mode (Autonomous Engineering)
Located in the **Builder** tab, this is the core autonomous agent loop. When you issue a command here (e.g., "Build a Python script that calculates Fibonacci numbers"), the IDE does the following:
1. **Plans:** Re-evaluates your goal and structures a list of acceptance criteria.
2. **Executes:** Uses the active local model (e.g., DeepSeek-R1) to iteratively write files, patch code, and run bash commands in an isolated sandbox.
3. **Tests & Heals:** Automatically executes unit tests. If a test fails, the agent will diagnose the error and rewrite the code, iterating up to a maximum of 10 times until the criteria pass.

### C. "Heretic Mode" (Uncensored Mode)
By toggling the **Heretic Mode** switch in the top right corner:
- The system bypasses all software engineering restrictions and guardrails.
- The default model dynamically swaps from deepseek-r1:7b to hermes3:8b (a fully uncensored model).
- Governance logging bypasses safety evaluation for maximum freedom.
- Use this mode when you need the agent to perform unrestricted research, creative tasks, or answer queries outside the strict domain of software development.

---

## 3. UI Features and Session Management

- **Session History:** The left sidebar automatically saves your past conversations and agent runs via LocalStorage. Click on any past session to re-hydrate the terminal and view the agent's previous logic.
- **New Chat:** Click + New Chat to clear the active context and start a fresh request. This prevents the agent from being confused by previous, unrelated code tasks.
- **File Attachments:** You can attach images, PDFs, or code files to your prompt using the paperclip icon. The backend will parse the content and supply it to the model.
- **Governance Modal:** Click the "Governance" button in the top right to view real-time metrics on your local sessions, including tokens spent, total compute time, and any sandbox violations the system blocked.

---

## 4. How to Swap and Configure Models

By default, Swarm IDE uses deepseek-r1:7b for reasoning tasks and hermes3:8b for Heretic mode. All models must be hosted locally via Ollama on port 11434.

If you wish to swap out the models (e.g., using a larger 14B model or a different coding model like qwen2.5-coder), you can easily update the variables in the backend.

### A. Swapping the Main Orchestrator Model
1. Open 6_builder_app.py in your text editor.
2. Locate the routing logic (around line 395):
   `python
   target_model = "hermes3:8b" if uncensored else "deepseek-r1:7b"
   `
3. Change "deepseek-r1:7b" to your desired Ollama model tag (e.g., "qwen2.5-coder:7b").

*Note: You will also want to update the default fallback in swarm-ide/backend/agents/orchestrator.py by changing DEFAULT_MODEL = "deepseek-r1:7b".*

### B. Swapping the specialized sub-agents
The IDE uses specialized smaller models for specific tasks to save compute. You can edit these in their respective agent files:

- **The Tester Agent** (Runs tests and diagnoses errors):
  Open swarm-ide/backend/agents/tester.py and modify:
  `python
  def diagnose_and_fix(..., model="qwen2.5-coder:7b"):
  `
- **The Librarian Agent** (Evaluates RAG context relevance):
  Open swarm-ide/backend/agents/librarian.py and modify:
  `python
  def evaluate_context(..., model="qwen2.5:1.5b"):
  `

### Important Hardware Note for Swapping
Swarm IDE was heavily optimized around the prompt structures and <think> token boundaries of **DeepSeek-R1**. If you swap to a non-reasoning model (like Llama 3), the agent may struggle to follow the strict XML action loop (<plan>, <write_file>, etc.). If you change the model, it is highly recommended to stick to reasoning models (-r1 variants) or models specifically fine-tuned for tool calling.


