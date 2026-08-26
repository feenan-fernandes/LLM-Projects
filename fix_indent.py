import re

with open('swarm-ide/backend/loop/builder_loop.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the specific block
bad_block_regex = r'\n                        elif action_type == "patch_file":.*?(?=\n            # 6\. WRITE FILE)'
bad_block = re.search(r'\n( +)elif action_type == "patch_file":', text)
if bad_block:
    indent = bad_block.group(1)
    
correct_block = '''
            elif action_type == "patch_file":
                path = args.get("path", "")
                diff_str = args.get("diff", "")
                workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workspace'))
                full_path = os.path.abspath(os.path.join(workspace_dir, path))
                
                path_safe = False
                try:
                    path_safe = os.path.commonpath([workspace_dir, full_path]) == workspace_dir
                except ValueError:
                    path_safe = False
                
                if not path_safe:
                    observation = f"Sandbox violation: Cannot write outside workspace directory."
                else:
                    try:
                        import patch as patch_lib
                        pset = patch_lib.fromstring(diff_str.encode('utf-8'))
                        success = pset.apply(root=os.path.dirname(full_path))
                        if success:
                            observation = f"Patch applied successfully to {path}"
                        else:
                            observation = f"Failed to apply patch to {path}. Context mismatch. Try <write_file> instead."
                    except Exception as e:
                        observation = f"Error applying patch to {path}: {e}"
'''

# Use replace based on exact string if regex is tricky
import ast
try:
    ast.parse(text)
except SyntaxError as se:
    print("Syntax error at", se.lineno, se.offset)
    lines = text.splitlines()
    for i in range(se.lineno-5, se.lineno+5):
        print(f"{i}: {lines[i-1]}")

