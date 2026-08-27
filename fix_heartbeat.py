with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

bad = '''                except queue.Empty:
                    # Heartbeat to trigger waitress client disconnect detection
                    yield json.dumps({"type": "ping"}) + '\\n'
                    
        except GeneratorExit:'''

good = '''                except queue.Empty:
                    # Heartbeat to trigger waitress client disconnect detection
                    yield json.dumps({"type": "ping", "pad": " " * 18000}) + '\\n'
                    
        except GeneratorExit:'''

if bad in text:
    text = text.replace(bad, good)
    with open('6_builder_app.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed heartbeat buffer issue")
else:
    print("Could not find bad block")
