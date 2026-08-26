import re

with open('swarm-ide/backend/loop/builder_loop.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('system_prompt=None', 'system_prompt=None,\\n    abort_event=None')

abort_check = '''
        if abort_event and abort_event.is_set():
            _emit({"type": "action", "iteration": iteration, "action": "abort", "result": "Task aborted by user."})
            return False, iteration, "Aborted by user"
'''
text = text.replace('for iteration in range(1, MAX_ITERATIONS + 1):', 'for iteration in range(1, MAX_ITERATIONS + 1):' + abort_check)

with open('swarm-ide/backend/loop/builder_loop.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text2 = f.read()

if 'abort_event=abort_evt' not in text2:
    text2 = text2.replace('def _stream():', 'def _stream():\\n        abort_evt = threading.Event()')
    text2 = text2.replace('system_prompt=custom_sys', 'system_prompt=custom_sys,\\n                            abort_event=abort_evt')
    text2 = text2.replace('except GeneratorExit:', 'except GeneratorExit:\\n                abort_evt.set()')
    
    # We also need to add except GeneratorExit to the while True: loop if it isn't there.
    # It currently does not have a try-except around q.get(). Let's add it.
    
    q_loop_old = '''            while True:
                item = q.get()
                if item.get('type') == 'finish':
                    yield json.dumps(item) + '\\n'
                    break
                yield json.dumps(item) + '\\n'
'''
    q_loop_new = '''            try:
                while True:
                    item = q.get()
                    if item.get('type') == 'finish':
                        yield json.dumps(item) + '\\n'
                        break
                    yield json.dumps(item) + '\\n'
            except GeneratorExit:
                abort_evt.set()
                raise
'''
    text2 = text2.replace(q_loop_old, q_loop_new)
    
    with open('6_builder_app.py', 'w', encoding='utf-8') as f:
        f.write(text2)
