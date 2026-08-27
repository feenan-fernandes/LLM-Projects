import os

path = 'swarm-ide/backend/loop/sandbox.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

bad = '''        else:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=run_cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )'''

good = '''        else:
            raise SandboxViolationError("CRITICAL: Docker is not available. Native host execution is disabled for security to prevent RCE. Please start Docker Desktop.")'''

if bad in text:
    text = text.replace(bad, good)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed RCE fallback")
else:
    print("Could not find block in sandbox")
