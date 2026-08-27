import json
import requests
import os

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "deepseek-r1:7b"

def load_system_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'orchestrator_system_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "You are the Orchestrator."

def call_orchestrator(conversation_context, model=DEFAULT_MODEL, temperature=0.1, mock_response=None, system_prompt=None, abort_event=None):
    """
    Calls the local Ollama instance with deepseek-r1:7b.
    Allows injecting a `mock_response` for isolated unit tests.
    """
    if mock_response:
        return mock_response, {'prompt_tokens': 0, 'completion_tokens': 0, 'eval_duration': 0}
        
    sys_prompt = system_prompt if system_prompt is not None else load_system_prompt()
    
    # Inject dynamic MCP tools if any exist
    try:
        from backend.loop.mcp_bridge import get_mcp_bridge
        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workspace'))
        bridge = get_mcp_bridge(workspace_dir)
        mcp_tools = bridge.get_tools_sync()
        if mcp_tools:
            mcp_docs = "\n\n=== DYNAMIC MCP TOOLS ===\nYou have access to the following external tools via MCP:\n"
            for t in mcp_tools:
                mcp_docs += f"Server: {t['server']} | Tool: {t['name']}\nDescription: {t['description']}\nSchema: {t['inputSchema']}\n\n"
            mcp_docs += "To use an MCP tool, use the following XML format:\n<mcp_call>\n{\"server\": \"<server_name>\", \"tool\": \"<tool_name>\", \"arguments\": { ... }}\n</mcp_call>\n"
            sys_prompt += mcp_docs
    except Exception as e:
        print(f"Failed to inject MCP tools: {e}")

    # Inject sub-agent tool
    sys_prompt += "\n\n=== SUB-AGENTS ===\nYou can delegate parallel research or isolated tasks to sub-agents. They will run in parallel and return their results.\n<spawn_worker>\n  <task>Read file X and summarize the functions</task>\n</spawn_worker>\nYou can output multiple <spawn_worker> blocks in a single response to spawn multiple parallel agents!\n"


    full_prompt = f"{sys_prompt}\n\n{conversation_context}"
    
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": temperature}
    }
    
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=900)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("response", ""), {
                'prompt_tokens': data.get('prompt_eval_count', 0),
                'completion_tokens': data.get('eval_count', 0),
                'eval_duration': data.get('eval_duration', 1)
            }
    except Exception as e:
        print(f"Orchestrator Model Error: {e}")
        
    return "", {'prompt_tokens': 0, 'completion_tokens': 0, 'eval_duration': 0}

def stream_orchestrator(conversation_context, model=DEFAULT_MODEL, temperature=0.1, system_prompt=None, abort_event=None):
    sys_prompt = system_prompt if system_prompt is not None else load_system_prompt()
    
    # Inject dynamic MCP tools if any exist
    try:
        from backend.loop.mcp_bridge import get_mcp_bridge
        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workspace'))
        bridge = get_mcp_bridge(workspace_dir)
        mcp_tools = bridge.get_tools_sync()
        if mcp_tools:
            mcp_docs = "\n\n=== DYNAMIC MCP TOOLS ===\nYou have access to the following external tools via MCP:\n"
            for t in mcp_tools:
                mcp_docs += f"Server: {t['server']} | Tool: {t['name']}\nDescription: {t['description']}\nSchema: {t['inputSchema']}\n\n"
            mcp_docs += "To use an MCP tool, use the following XML format:\n<mcp_call>\n{\"server\": \"<server_name>\", \"tool\": \"<tool_name>\", \"arguments\": { ... }}\n</mcp_call>\n"
            sys_prompt += mcp_docs
    except Exception as e:
        print(f"Failed to inject MCP tools: {e}")

    # Inject sub-agent tool
    sys_prompt += "\n\n=== SUB-AGENTS ===\nYou can delegate parallel research or isolated tasks to sub-agents. They will run in parallel and return their results.\n<spawn_worker>\n  <task>Read file X and summarize the functions</task>\n</spawn_worker>\nYou can output multiple <spawn_worker> blocks in a single response to spawn multiple parallel agents!\n"


    full_prompt = f"{sys_prompt}\n\n{conversation_context}"
    
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": True,
        "options": {"temperature": temperature}
    }
    
    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=900) as resp:
            if resp.status_code == 200:
                for line in resp.iter_lines():
                    if line:
                        yield json.loads(line.decode('utf-8'))
    except Exception as e:
        print(f"Orchestrator Stream Error: {e}")
