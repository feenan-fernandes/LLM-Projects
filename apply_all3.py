with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

# 1. Threading import
if 'import threading' not in text:
    text = text.replace('app = Flask(__name__)', 'app = Flask(__name__)\nimport threading\nbuild_lock = threading.Lock()\n')

# 2. Waitress
text = text.replace("app.run(host='0.0.0.0', port=5000)", "from waitress import serve\n    print('Production WSGI Server active on http://127.0.0.1:5000')\n    serve(app, host='127.0.0.1', port=5000)")

# 3. Replace _stream() body with try/finally
start_marker = "    def _stream():\n"
end_marker = "    return Response(_stream(), mimetype='application/x-ndjson')"

parts = text.split(start_marker)
before = parts[0]
after_start = parts[1]
body_parts = after_start.split(end_marker)
body = body_parts[0]
after_body = body_parts[1]

indented_body = ""
for line in body.splitlines():
    indented_body += "    " + line + "\n"

indented_body = indented_body.replace("system_prompt=custom_sys", "system_prompt=custom_sys, abort_event=abort_evt")
indented_body = indented_body.replace("system_prompt=clean_sys", "system_prompt=clean_sys, abort_event=abort_evt")
indented_body = indented_body.replace("system_prompt=custom_sys\n", "system_prompt=custom_sys, abort_event=abort_evt\n")

new_stream_function = start_marker + '''        abort_evt = threading.Event()
        if not build_lock.acquire(blocking=False):
            yield json.dumps({'type': 'finish', 'status': 'blocked', 'summary': 'Server is busy processing another Swarm task. Please wait.'}) + '\\n'
            return
        
        try:
''' + indented_body + '''        except GeneratorExit:
            abort_evt.set()
            raise
        finally:
            build_lock.release()
            
''' + end_marker

final_text = before + new_stream_function + after_body

with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.write(final_text)
