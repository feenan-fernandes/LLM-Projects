import os

path = 'swarm-ide/backend/agents/skill_installer.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

bad = '''    slug = candidate["slug"]
    skill_md = candidate.get("skill_md", "")'''

good = '''    import werkzeug.utils
    slug = werkzeug.utils.secure_filename(candidate["slug"])
    if not slug:
        raise ValueError("Invalid skill slug.")
    skill_md = candidate.get("skill_md", "")'''

if bad in text:
    text = text.replace(bad, good)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed Path Traversal")
else:
    print("Could not find block in skill_installer")
