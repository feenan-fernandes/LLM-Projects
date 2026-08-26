with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_stream = False
found_app = False

for line in lines:
    if "app = Flask(__name__)" in line and not found_app:
        new_lines.append(line)
        new_lines.append("import threading\nbuild_lock = threading.Lock()\n")
        found_app = True
        continue
        
    if line.startswith("    def _stream():"):
        in_stream = True
        new_lines.append(line)
        new_lines.append("        if not build_lock.acquire(blocking=False):\n")
        new_lines.append("            yield json.dumps({'type': 'finish', 'status': 'blocked', 'summary': 'Server is busy processing another Swarm task. Please wait.'}) + '\\n'\n")
        new_lines.append("            return\n")
        new_lines.append("        try:\n")
        continue
        
    if line.startswith("    return Response(_stream()"):
        in_stream = False
        new_lines.append("        finally:\n")
        new_lines.append("            build_lock.release()\n")
        new_lines.append(line)
        continue
        
    if in_stream:
        # indent by 4 spaces
        new_lines.append("    " + line)
    else:
        new_lines.append(line)

with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

