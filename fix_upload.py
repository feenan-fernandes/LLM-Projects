import re

with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

secure_import = '''
from werkzeug.utils import secure_filename
'''
text = text.replace('import base64\\nimport io', 'import base64\\nimport io\\n' + secure_import.strip())

parse_doc_old = '''def parse_document(name, b64_content):'''
parse_doc_new = '''def parse_document(name, b64_content):
    name = secure_filename(name)
    if not name: name = "unnamed_file"'''
text = text.replace(parse_doc_old, parse_doc_new)

with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed unsanitized file upload.")
