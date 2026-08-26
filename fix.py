import re
with open('swarm-ide/backend/loop/builder_loop.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r' +elif action_type == "patch_file":', '            elif action_type == "patch_file":', text)

with open('swarm-ide/backend/loop/builder_loop.py', 'w', encoding='utf-8') as f:
    f.write(text)
