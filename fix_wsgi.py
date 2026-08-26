with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("app.run(host='0.0.0.0', port=5000)", "from waitress import serve\\n    print('Production WSGI Server active on http://127.0.0.1:5000')\\n    serve(app, host='127.0.0.1', port=5000)")

with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.write(text)
