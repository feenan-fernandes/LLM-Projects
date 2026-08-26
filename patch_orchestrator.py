with open('swarm-ide/backend/agents/orchestrator.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("def stream_orchestrator(conversation_context, model=DEFAULT_MODEL, temperature=0.1, system_prompt=None):", "def stream_orchestrator(conversation_context, model=DEFAULT_MODEL, temperature=0.1, system_prompt=None, abort_event=None):")
text = text.replace("def call_agent(model, prompt, temperature=0.1, mock_response=None):", "def call_agent(model, prompt, temperature=0.1, mock_response=None, abort_event=None):")
text = text.replace("def call_orchestrator(conversation_context, model=DEFAULT_MODEL, temperature=0.1, mock_response=None, system_prompt=None):", "def call_orchestrator(conversation_context, model=DEFAULT_MODEL, temperature=0.1, mock_response=None, system_prompt=None, abort_event=None):")

# Inside stream_orchestrator, we loop over r.iter_lines()
# We should add: if abort_event and abort_event.is_set(): break
stream_loop = '''    with requests.post(OLLAMA_API_URL, json=payload, stream=True) as r:
        for line in r.iter_lines():'''
stream_loop_new = '''    with requests.post(OLLAMA_API_URL, json=payload, stream=True) as r:
        for line in r.iter_lines():
            if abort_event and abort_event.is_set():
                break'''
text = text.replace(stream_loop, stream_loop_new)

with open('swarm-ide/backend/agents/orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(text)
