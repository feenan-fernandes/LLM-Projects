import os
import re

with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. We need to stop appending the raw 'prompt' (which has --- ATTACHED FILES ---) to the session journal.
# We should only append the base prompt without files.
# But wait, prompt is modified in uild()!

# Let's just fix the prompt logic.
new_text = text.replace("prompt += f\"\\n\\n[File: {f.get('name')}]\\n{parsed_text}\\n\"", "prompt += f\"\\n\\n[File: {f.get('name')}]\\n{parsed_text}\\n\"")
# Wait, actually, let's truncate the string passed to append_entry.
new_text = new_text.replace("append_entry(task_id, prompt, target_model)", "append_entry(task_id, data.get('prompt', '')[:1000] + (' (Files attached)' if data.get('files') else ''), target_model)")

# 2. We need to pass history to run_builder_loop!
new_text = new_text.replace("prompt,\n                        task_id=task_id,", "prompt,\n                        task_id=task_id,\n                        history=history,")

with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

# Also update swarm-ide/backend/loop/builder_loop.py run_builder_loop signature to handle history properly.
with open('swarm-ide/backend/loop/builder_loop.py', 'r', encoding='utf-8') as f:
    builder_text = f.read()

if "def run_builder_loop(" in builder_text and "history=None" not in builder_text.split("def run_builder_loop(")[1][:500]:
    builder_text = builder_text.replace("def run_builder_loop(\n    task_description,", "def run_builder_loop(\n    task_description,\n    history=None,")
    # Now we need to inject history into the prompt
    inject = '''
    if history:
        hist_str = "\\n\\n--- PREVIOUS CONVERSATION ---\\n"
        for turn in history:
            hist_str += f"{turn['role'].upper()}: {turn['content']}\\n"
        hist_str += "--- END PREVIOUS CONVERSATION ---\\n"
        task_description = hist_str + task_description
'''
    # Find the beginning of run_builder_loop logic
    builder_text = builder_text.replace("    if mock_responses is None:", inject + "\n    if mock_responses is None:")

with open('swarm-ide/backend/loop/builder_loop.py', 'w', encoding='utf-8') as f:
    f.write(builder_text)

