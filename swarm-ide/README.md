# Swarm IDE v2.0 — Autonomous Builder

A fully local, privacy-first, multi-agent autonomous software engineering environment built on Ollama.

## Architecture

```
swarm-ide/
├── backend/
│   ├── prompts/
│   │   └── orchestrator_system_prompt.txt     # Literal system prompt for deepseek-r1:7b
│   ├── agents/
│   │   ├── orchestrator.py                    # deepseek-r1:7b — reasoning & planning
│   │   ├── librarian.py                       # qwen2.5:3b    — binary relevance grading
│   │   ├── tester.py                          # qwen2.5-coder:7b — debug & self-heal
│   │   ├── skill_scout.py                     # GitHub search + YAML frontmatter scoring
│   │   └── skill_installer.py                 # Post-approval disk write + registry update
│   ├── loop/
│   │   ├── action_parser.py                   # XML tag extractor (write_file/execute_bash/run_test/select_skill/finish)
│   │   ├── builder_loop.py                    # 8-iteration state machine
│   │   └── sandbox.py                         # Pre-execution blocklist gate → governance.db
│   ├── skills/
│   │   ├── registry.json                      # Installed skills index
│   │   └── {slug}/SKILL.md                    # Sparse-checked-out skills
│   ├── governance/
│   │   ├── governance.db                      # SQLite trajectory log
│   │   └── logger.py                          # log_action(task_id, iteration, action_type, content, tokens, latency_ms)
│   └── rag/
│       ├── chroma_client.py
│       └── ingest.py                          # PyMuPDF, Pandas, PyTesseract
└── frontend/
    └── components/
        ├── FlowchartHUD.tsx                   # Live node-by-node pipeline visualiser
        ├── SkillPanel.tsx                     # Shows discovered/installed/selected skills
        └── ArtifactCard.tsx                   # Plan/diff review cards with Approve/Reject

```

## Hard Constraints (enforced in code)

| Constraint | Implementation |
|---|---|
| 100% local inference | All LLM calls go to `http://127.0.0.1:11434` only |
| ≤7B parameters per model | Hardcoded model names in each agent wrapper |
| No destructive commands | `sandbox.py` blocklist fires *before* `subprocess.run()` |
| Governance-first | `governance.db` is wired in from Phase 4.1, before any other module |
| Human-in-the-loop for installs | `skill_installer.py` is never called without an explicit `onApprove` callback |

## Models

| Role | Model | Notes |
|---|---|---|
| Orchestrator | `deepseek-r1:7b` | Reasoning + XML action loop |
| Librarian | `qwen2.5:3b` | Binary YES/NO relevance grading |
| Tester | `qwen2.5-coder:7b` | Self-heal code repair |
| Tester fallback | `deepseek-coder:7b` | Configurable swap for speed |
| Heretic | (user-toggled, must be ≤7B) | Uncensored fallback |

## Acceptance Test Results

| Phase | Test | Result |
|---|---|---|
| 4.1 | Governance + Sandbox | PASS |
| 4.2 | Builder Loop (≤3 iterations) | PASS |
| 4.3 | Skill Discovery + Librarian grading | PASS |
| 4.4 | Skill install + context injection | PASS |
| 4.5 | Self-heal within 3 iterations | PASS |

## Running Tests

```bash
cd swarm-ide
python test_4_1.py      # Governance & Sandbox
python test_4_2.py      # Builder State Machine
python test_4_3.py      # GitHub Skill Discovery (mocked)
python test_4_4_4_5.py  # Skill Install + Self-Heal
```
