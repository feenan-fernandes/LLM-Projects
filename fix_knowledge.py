import re

with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the knowledge branch
old_knowledge_branch = '''        elif task_type == "knowledge":
            from backend.agents.orchestrator import stream_orchestrator
            
            q_prompt = (
                "You are an expert assistant. The user has asked a question or provided a document. "
                "Answer the user's request conversationally based on the context provided. Do NOT use XML tags, just output the answer.\\n\\n"
                f"{prompt}"
            )'''

new_knowledge_branch = '''        elif task_type == "knowledge":
            from backend.agents.orchestrator import stream_orchestrator
            
            clean_sys = custom_sys or "You are an expert AI assistant. Answer the user conversationally and accurately. Do not use XML tags."
            
            hist_str = "\\n--- PREVIOUS CONVERSATION ---\\n"
            for turn in history:
                hist_str += f"{turn.get('role', '').upper()}: {turn.get('content', '')}\\n"
            hist_str += "--- END PREVIOUS CONVERSATION ---\\n" if history else ""
            
            q_prompt = (
                f"{hist_str}\\n"
                "The user has asked a question or provided a document. "
                "Answer the user's request based on the context provided.\\n\\n"
                f"User: {prompt}"
            )
'''
text = text.replace(old_knowledge_branch, new_knowledge_branch)

# Update the stream_orchestrator call to use clean_sys
text = text.replace('stream_orchestrator(q_prompt, model=target_model, system_prompt=custom_sys)', 'stream_orchestrator(q_prompt, model=target_model, system_prompt=clean_sys)')

with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed knowledge branch context!")
