with open('swarm-ide/backend/loop/builder_loop.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\\n', '\n')
with open('swarm-ide/backend/loop/builder_loop.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text2 = f.read()
text2 = text2.replace('\\n', '\n')
with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.write(text2)
