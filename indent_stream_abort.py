with open('6_builder_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_stream = False

for line in lines:
    if line.startswith("    def _stream():"):
        in_stream = True
        new_lines.append(line)
        new_lines.append("        abort_evt = threading.Event()\n")
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
        # We need to catch GeneratorExit in the while True loop
        if line.startswith("            while True:"):
            new_lines.append("            try:\n")
            new_lines.append("    " + line)
        elif line.startswith("                item = q.get()"):
            new_lines.append("    " + line)
        elif line.startswith("                if item.get('type') == 'finish':"):
            new_lines.append("    " + line)
        elif line.startswith("                    yield json.dumps(item) + '\\n'"):
            new_lines.append("    " + line)
        elif line.startswith("                    break"):
            new_lines.append("    " + line)
        elif line.startswith("                yield json.dumps(item) + '\\n'"):
            new_lines.append("    " + line)
            new_lines.append("            except GeneratorExit:\n")
            new_lines.append("                abort_evt.set()\n")
            new_lines.append("                raise\n")
        else:
            # We must pass abort_evt to run_builder_loop
            if "system_prompt=custom_sys" in line and "run_builder_loop" in "".join(lines):
                # actually it's easier to just append it
                new_lines.append("    " + line.replace("system_prompt=custom_sys", "system_prompt=custom_sys, abort_event=abort_evt"))
            elif "stream_orchestrator(" in line:
                new_lines.append("    " + line.replace("system_prompt=clean_sys", "system_prompt=clean_sys"))
            else:
                new_lines.append("    " + line)
    else:
        new_lines.append(line)

with open('6_builder_app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

