import os

path = 'swarm-ide/backend/loop/builder_loop.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

bad = '''def _human_approval_pending(action):'''

good = '''import py_compile
def validate_file(path):
    if not path.endswith('.py'): return None
    try:
        py_compile.compile(path, doraise=True)
        return None
    except Exception as e:
        return "Syntax Error in file: " + str(e)

def _human_approval_pending(action):'''

if bad in text:
    text = text.replace(bad, good)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed validate_file")
else:
    print("Could not find block in builder_loop")
