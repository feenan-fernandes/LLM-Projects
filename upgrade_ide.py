import os
import re

print("Upgrading Swarm IDE...")

# 1. Update action_parser.py
parser_path = "swarm-ide/backend/loop/action_parser.py"
with open(parser_path, "r", encoding="utf-8") as f:
    parser_code = f.read()

if "<replace_block>" not in parser_code:
    replace_block_logic = '''
    if "<replace_block>" in xml_text:
        return {"type": "replace_block", "args": {
            "path": _extract(xml_text, "path") or "",
            "search": _extract(xml_text, "search") or "",
            "replace": _extract(xml_text, "replace") or "",
        }}
'''
    parser_code = parser_code.replace('    if "<patch_file>" in xml_text:', replace_block_logic + '    if "<patch_file>" in xml_text:')
    with open(parser_path, "w", encoding="utf-8") as f:
        f.write(parser_code)
    print("Added <replace_block> to action_parser.py")

# 2. Update builder_loop.py
builder_path = "swarm-ide/backend/loop/builder_loop.py"
with open(builder_path, "r", encoding="utf-8") as f:
    builder_code = f.read()

if "def _truncate_output" not in builder_code:
    truncate_func = '''
def _truncate_output(text: str, max_chars: int = 3000) -> str:
    if not text: return ""
    if len(text) <= max_chars: return text
    half = max_chars // 2
    return text[:half] + "\\n\\n... [OUTPUT TRUNCATED to protect context window. Use grep to search] ...\\n\\n" + text[-half:]

'''
    builder_code = builder_code.replace("def run_builder_loop", truncate_func + "def run_builder_loop")
    
    # Apply truncation to execute_bash
    builder_code = builder_code.replace(
        "observation = f\"STDOUT:\\n{res['stdout']}\\nSTDERR:\\n{res['stderr']}\\nExit: {res['code']}\"",
        "observation = f\"STDOUT:\\n{_truncate_output(res['stdout'])}\\nSTDERR:\\n{_truncate_output(res['stderr'])}\\nExit: {res['code']}\""
    )
    
    # Apply truncation to use_skill
    builder_code = builder_code.replace(
        "observation = f\"Skill Execution STDOUT:\\n{res['stdout']}\\nSTDERR:\\n{res['stderr']}\\nExit: {res['code']}\"",
        "observation = f\"Skill Execution STDOUT:\\n{_truncate_output(res['stdout'])}\\nSTDERR:\\n{_truncate_output(res['stderr'])}\\nExit: {res['code']}\""
    )
    
    # Replace block logic
    replace_block_logic = '''
            elif action_type == "replace_block":
                path = args.get("path", "")
                search = args.get("search", "")
                replace = args.get("replace", "")
                workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workspace'))
                full_path = os.path.abspath(os.path.join(workspace_dir, path))
                
                try:
                    path_safe = os.path.commonpath([workspace_dir, full_path]) == workspace_dir
                except ValueError:
                    path_safe = False
                
                if not path_safe:
                    observation = f"Sandbox violation: Cannot write outside workspace directory."
                else:
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        if search not in content:
                            observation = f"Failed to patch: The exact search block was not found in {path}. Make sure whitespace matches exactly."
                        else:
                            content = content.replace(search, replace, 1)
                            with open(full_path, "w", encoding="utf-8") as f:
                                f.write(content)
                            observation = f"Successfully replaced block in {path}."
                    except Exception as e:
                        observation = f"Error reading/writing {path}: {e}"
'''
    builder_code = builder_code.replace('            elif action_type == "write_file":', replace_block_logic + '            elif action_type == "write_file":')
    
    # Also add path safety to patch_file
    builder_code = re.sub(
        r'try:\s*import patch as patch_lib\s*pset = patch_lib\.fromstring\(diff_str\.encode\(\'utf-8\'\)\)\s*success = pset\.apply\(root=os\.path\.dirname\(full_path\)\)',
        r'''try:
                    path_safe = os.path.commonpath([workspace_dir, full_path]) == workspace_dir
                except ValueError:
                    path_safe = False
                if not path_safe:
                    observation = f"Sandbox violation: Cannot write outside workspace directory."
                else:
                    try:
                        import patch as patch_lib
                        pset = patch_lib.fromstring(diff_str.encode('utf-8'))
                        success = pset.apply(root=os.path.dirname(full_path))''',
        builder_code
    )
    
    with open(builder_path, "w", encoding="utf-8") as f:
        f.write(builder_code)
    print("Added output truncation, path safety, and <replace_block> to builder_loop.py")

print("Done!")
