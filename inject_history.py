import sys
with open('swarm-ide/backend/loop/builder_loop.py', 'r', encoding='utf-8') as f:
    text = f.read()

inject = '''
    if history:
        hist_str = "\\n\\n--- PREVIOUS CONVERSATION ---\\n"
        for turn in history:
            hist_str += f"{turn['role'].upper()}: {turn['content']}\\n"
        hist_str += "--- END PREVIOUS CONVERSATION ---\\n"
        task_description = hist_str + task_description
'''

if '--- PREVIOUS CONVERSATION ---' not in text:
    text = text.replace('    if mock_responses is None:', inject + '\n    if mock_responses is None:')
    with open('swarm-ide/backend/loop/builder_loop.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Injected!")
else:
    print("Already injected")
