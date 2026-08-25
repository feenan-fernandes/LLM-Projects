content = open('backend/prompts/orchestrator_system_prompt.txt', encoding='utf-8').read()
checks = [
    'Skill-Scout',
    'maximum 8 iterations',
    'search_github_skills',
    'evaluate_skill',
    'install_skill',
    'self_heal',
    '<finish>',
    'HARD RULES',
    'Heretic Mode never overrides rules 1',
    'Never fabricate a GitHub repo',
]
all_ok = True
for c in checks:
    found = c in content
    status = "OK" if found else "MISSING"
    print(f"  [{status}] {c}")
    if not found:
        all_ok = False

print()
print("Prompt verbatim check:", "PASS" if all_ok else "FAIL")
