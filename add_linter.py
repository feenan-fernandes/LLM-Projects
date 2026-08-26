import re

with open('swarm-ide/backend/loop/builder_loop.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add a generic validate_file helper
validator_code = '''
def validate_file(path):
    if not path.endswith('.py'): return None
    try:
        import py_compile
        py_compile.compile(path, doraise=True)
        return None
    except Exception as e:
        return f"SYNTAX ERROR CAUGHT BY AUTO-LINTER: {e}"

def extract_xml_tag(text, tag):
'''
text = text.replace('def extract_xml_tag(text, tag):', validator_code)

# Inject into patch_file
text = text.replace('observation = f"Patch applied successfully to {path}"', 'observation = f"Patch applied successfully to {path}"\\n                            err = validate_file(full_path)\\n                            if err: observation += "\\n" + err')

# Inject into replace_block
text = text.replace('observation = f"Successfully replaced block in {path}."', 'observation = f"Successfully replaced block in {path}."\\n                            err = validate_file(full_path)\\n                            if err: observation += "\\n" + err')

# Inject into write_file
text = text.replace('observation = f"File written: {path}"', 'observation = f"File written: {path}"\\n                    err = validate_file(full_path)\\n                    if err: observation += "\\n" + err')

with open('swarm-ide/backend/loop/builder_loop.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Added syntax validation.")
