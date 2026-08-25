import os
with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = \"\"\"def agent_tester(original_code, error_trace):
    prompt = f"You are an elite Python debugger. The following code threw an error. Fix it. If the error is a missing module (ModuleNotFoundError), rewrite the code to use built-in Python standard libraries instead. Return ONLY the corrected code inside a single \\\python code block.\\n\\nCode:\\n{original_code}\\n\\nError:\\n{error_trace}"
    resp, metrics = call_agent(TESTER, prompt, temperature=0.1)
    fixed_code = extract_code_block(resp)
    return fixed_code if fixed_code else original_code\"\"\"

new_funcs = \"\"\"def get_swarm_memory():
    try:
        return client.get_or_create_collection(name='swarm_healing_memory', embedding_function=default_ef)
    except:
        return None

def swarm_heal(original_code, initial_error):
    mem_col = get_swarm_memory()
    current_code = original_code
    current_error = initial_error
    history = \"\"
    
    for attempt in range(3):
        # 1. Recall Learning
        past_learnings = \"\"
        if mem_col:
            try:
                res = mem_col.query(query_texts=[current_error], n_results=1)
                if res and res['documents'] and res['documents'][0]:
                    past_learnings = res['documents'][0][0]
            except: pass
            
        mem_injection = f\"\\n\\nPAST LEARNINGS (Similar Errors we fixed before):\\n{past_learnings}\" if past_learnings else \"\"
        
        # 2. Diagnostician (DeepSeek-R1)
        diag_prompt = f\"You are the Diagnostician. Analyze this broken code and error. Give a short Root Cause Analysis (RCA) and a strategy to fix it. If missing a module, plan to use standard libraries.{mem_injection}\\n\\nCode:\\n{current_code}\\n\\nError:\\n{current_error}\\n\\nFailed History:\\n{history}\"
        rca_resp, _ = call_agent(ORCHESTRATOR, diag_prompt, temperature=0.3)
        if \"</think>\" in rca_resp:
            rca_resp = rca_resp.split(\"</think>\")[-1].strip()
            
        # 3. Coder (Qwen2.5-Coder)
        coder_prompt = f\"You are the Coder. Implement the fix based on the Diagnostician's RCA. Return ONLY the corrected code inside a \\\python block.\\n\\nOriginal Code:\\n{current_code}\\n\\nDiagnostician RCA:\\n{rca_resp}\"
        code_resp, _ = call_agent(TESTER, coder_prompt, temperature=0.1)
        fixed_code = extract_code_block(code_resp) or current_code
        
        # 4. Validator Sandbox
        success, err_msg = run_sandbox(fixed_code)
        if success:
            if mem_col:
                try:
                    import uuid
                    doc_id = \"mem_\" + uuid.uuid4().hex[:8]
                    doc = f\"ERROR:\\n{initial_error}\\n\\nRCA:\\n{rca_resp}\\n\\nFIX:\\n{fixed_code}\"
                    mem_col.add(ids=[doc_id], documents=[doc], metadatas=[{\"type\": \"heal\"}])
                except: pass
            return True, fixed_code, f\"Multi-agent Swarm healed code after {attempt+1} passes.\"
        else:
            history += f\"\\nAttempt {attempt+1} Failed. New Error: {err_msg[:200]}\"
            current_code = fixed_code
            current_error = err_msg
            
    return False, current_code, f\"Swarm exhausted all attempts. Final Error: {current_error[:50]}\"\"\"\"

content = content.replace(old_func, new_funcs)

with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(\"Replaced function\")
