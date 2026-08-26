with open('swarm-ide/backend/loop/builder_loop.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        if 'elif action_type ==' in line or 'if action_type ==' in line:
            print(line.strip())
