with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

bad = '''                try:
                    ev = q.get(timeout=1.0)
                    if ev is None:
                        break
                    if ev.get('type') == 'finish':
                        governance_logger.end_session(task_id, ev.get('status', 'SUCCESS').upper())
                    yield json.dumps(ev) + '\\n'
    
        except GeneratorExit:'''

good = '''                try:
                    ev = q.get(timeout=1.0)
                    if ev is None:
                        break
                    if ev.get('type') == 'finish':
                        governance_logger.end_session(task_id, ev.get('status', 'SUCCESS').upper())
                    yield json.dumps(ev) + '\\n'
                except queue.Empty:
                    yield json.dumps({'type': 'ping'}) + '\\n'
                    
        except GeneratorExit:'''

if bad in text:
    text = text.replace(bad, good)
    with open('6_builder_app.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed syntax error")
else:
    print("Could not find bad block")
