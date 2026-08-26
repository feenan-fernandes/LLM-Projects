with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# I already lost the threading lock changes because I checked out!
# So I need to apply:
# 1. Threading import & lock
# 2. _stream() abort & lock logic
# 3. Waitress WSGI

import_threading = "import threading\\nbuild_lock = threading.Lock()\\n"
if "build_lock = threading.Lock()" not in text:
    text = text.replace("app = Flask(__name__)", "app = Flask(__name__)\\n" + import_threading)

# Waitress WSGI
text = text.replace("app.run(host='0.0.0.0', port=5000)", '''from waitress import serve
    print('Production WSGI Server active on http://127.0.0.1:5000')
    serve(app, host='127.0.0.1', port=5000)''')

with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.write(text)

# Let's use the indent_stream logic but add abort_evt!
