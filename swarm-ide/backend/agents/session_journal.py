"""
session_journal.py — Phase 0.3
Lightweight cross-session working memory using a structured Markdown journal.
Appends a task summary after each run; injects the last N entries into the
next session's Orchestrator context.

Pattern: agentmemory (SQLite FTS5 + JSON journals), adapted for filesystem.
"""
import os
import json
from datetime import datetime, timezone

JOURNAL_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'workspace', 'task_journal.md'
)
MAX_INJECT_ENTRIES = 3


def _ensure_journal():
    path = os.path.abspath(JOURNAL_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# Swarm IDE — Task Journal\n\n")
    return path


def append_entry(task_id: str, task: str, status: str, summary: str, iterations: int, tokens: int = 0):
    """Appends a structured entry to task_journal.md after a task completes."""
    path = _ensure_journal()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = (
        f"\n---\n"
        f"## [{ts}] task_id: `{task_id}`\n"
        f"**Task:** {task}\n"
        f"**Status:** `{status}` | **Iterations:** {iterations} | **Tokens:** {tokens}\n"
        f"**Summary:** {summary}\n"
    )
    with open(path, 'a', encoding='utf-8') as f:
        f.write(entry)


def get_recent_context(n: int = MAX_INJECT_ENTRIES) -> str:
    """
    Reads the last N journal entries and returns them as a formatted string
    ready for injection into the Orchestrator's working context.
    """
    path = _ensure_journal()
    try:
        with open(path, encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return ""

    # Split on the --- separator, skip the header
    entries = [e.strip() for e in content.split("---") if "task_id:" in e]
    recent = entries[-n:] if len(entries) >= n else entries

    if not recent:
        return ""

    header = f"[RECENT TASK HISTORY — last {len(recent)} session(s)]"
    return header + "\n" + "\n".join(recent)
