# Swarm IDE: Modern UI/UX Architecture Blueprint

As an AI Pentester and System Design Expert, I have evaluated the current frontend implementation (	emplates/index.html). Currently, it relies on a monolithic Vanilla JavaScript script coupled directly to Flask Jinja templates. While functional, it suffers from state-management brittleness (e.g., Base64 strings polluting prompt contexts, race conditions in streaming, and a lack of proper session compartmentalization).

To elevate Swarm IDE to the standard of **Hermes**, **Perplexity**, or **Antigravity 2.0**, the frontend must be decoupled and modernized. Even for a completely local, air-gapped tool, the UI must feel instantly responsive, spatially aware, and transparent about agent actions.

Here is the architectural and design blueprint for a V2 UI.

---

## 1. Core Technology Stack
- **Framework:** React 18+ (via Vite) or Vue 3. 
- **Styling:** TailwindCSS for utility-first, highly responsive design with deep Dark Mode support (#0d1117 GitHub dark palette).
- **State Management:** Zustand (React) or Pinia (Vue) for tracking streaming states, active agents, and sandbox health without prop-drilling.
- **Markdown & Syntax:** eact-markdown + emark-gfm + highlight.js (for rendering agent code outputs with one-click "Copy" or "Apply to File" buttons).

## 2. Spatial Layout & Layout Geometry
A modern AI IDE requires a 3-pane layout to balance chat with context:

### Left Sidebar: Context & Sessions
- **New Workspace / New Chat:** Clear CTA at the top.
- **Session History:** Grouped by "Today", "Previous 7 Days". Clicking a session instantly loads the conversation JSON from the local SQLite governance_logger.py database (rather than fragile localStorage).
- **Global Toggles:** Quick access toggles for Heretic Mode (Uncensored), Model Selector (Hermes/Deepseek), and Docker Sandbox Status (Green dot = Active, Red dot = Subprocess Fallback).

### Center Pane: The Chat Canvas
- **Sticky Input Bar:** A large, multi-line text area pinned to the bottom. Supports /slash commands (e.g., /clear, /deploy) natively with a pop-up autocomplete menu.
- **Drag & Drop Zone:** Dropping files here doesn't convert them to raw Base64 in the text box. Instead, they render as sleek "pills" (e.g., 📄 app.py (2kb) [x]). The backend uploads these to a temporary workspace/.staging/ directory for the LLM to access.
- **Message Rendering:** 
  - User messages are right-aligned.
  - Agent messages are left-aligned.

### Right Sidebar (Collapsible): Agent Telemetry & Workspace
- **Live File Tree:** A real-time view of the workspace/ directory using WebSockets. When the agent creates or patches a file, it flashes yellow.
- **Action Feed:** A live, scrolling terminal-like feed of exactly what the agent is doing under the hood (e.g., [SYS] Executing bash: pytest, [SYS] Patching: app.py). This keeps the main chat canvas clean while satisfying power users.

## 3. Advanced UX Paradigms

### A. The "Chain of Thought" Accordion
Models like DeepSeek-R1:7b natively output massive <think>...</think> blocks. 
- **The Problem:** Dumping 2,000 words of raw XML reasoning into the UI overwhelms the user.
- **The UX Fix:** The UI should parse out the <think> tag and render it as a collapsible, sleek accordion: [+] Agent Reasoning (12.4s). By default, it is collapsed, showing only the final conversational output and tool calls.

### B. Interactive Tool Cards
When the agent outputs an XML tool call like <execute_bash><command>npm test</command></execute_bash>, the UI should **intercept** this before it renders as raw text.
- **The UX Fix:** Render a React component:
  `html
  <div class="tool-card">
    <span>🛠️ Terminal: npm test</span>
    <button>View Output</button>
  </div>
  `
This is exactly how Antigravity handles hidden bash commands, reducing cognitive load.

### C. State-Aware Loading States
Instead of a generic spinner, the UI should use Server-Sent Events (SSE) to display exactly what the agent loop is doing:
- *Thinking...*
- *Reading repo_map.py...*
- *Running sandbox...*
- *Testing fixes...*

## 4. Implementation Steps (Migration Path)
1. **API Decoupling:** Move 6_builder_app.py entirely to JSON REST / SSE endpoints. Remove ender_template('index.html').
2. **Initialize Vite:** Run 
pm create vite@latest frontend -- --template react-ts.
3. **Build the Chat Component:** Implement the custom Markdown renderer that intercepts <think> and <execute_bash> tags to render rich UI components instead of raw text.
4. **WebSocket/SSE Integration:** Pipe the governance_logger directly to the frontend's Right Sidebar for real-time observability.
