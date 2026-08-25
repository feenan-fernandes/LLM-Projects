"""
agentless_loop.py — Phase 4
Two-phase Localise-then-Repair fast-path for bug-fix tasks.
Inspired by Agentless (UIUC, arXiv:2407.01489).

Activates when the Librarian classifies a task as FIX/BUG (narrow scope).
Completes in ≤3 iterations, preserving the 8-iteration budget for BUILD tasks.
"""
import os
import re

from backend.agents.orchestrator import call_orchestrator
from backend.agents.tester import diagnose_and_fix
from backend.loop.sandbox import execute_command_safely, SandboxViolationError
from backend.governance.logger import log_action
from backend.rag.repo_map import build_repo_map

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workspace')


def _localise(task: str, repo_map: str, model_mock=None, model="deepseek-r1:7b") -> dict:
    """
    Phase 1: Ask the Orchestrator to identify the suspect file and line range.
    Returns {file, start_line, end_line, reasoning}.
    """
    prompt = (
        f"TASK: {task}\n\n"
        f"REPO MAP:\n{repo_map}\n\n"
        "Identify the single most likely file and line range that contains the bug. "
        "Output ONLY:\n"
        "FILE: <relative path>\n"
        "LINES: <start>-<end>\n"
        "REASON: <one sentence>"
    )
    response, metrics = call_orchestrator(prompt, mock_response=model_mock, model=model)
    file_m = re.search(r"FILE:\s*(.+)", response)
    lines_m = re.search(r"LINES:\s*(\d+)-(\d+)", response)
    reason_m = re.search(r"REASON:\s*(.+)", response)

    return {
        "file": file_m.group(1).strip() if file_m else "",
        "start_line": int(lines_m.group(1)) if lines_m else 1,
        "end_line": int(lines_m.group(2)) if lines_m else 50,
        "reasoning": reason_m.group(1).strip() if reason_m else "",
        "metrics": metrics,
    }


def _read_span(filepath: str, start: int, end: int) -> str:
    """Reads a specific line span from a file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
        span = lines[max(0, start - 1):end]
        return "".join(span)
    except Exception as e:
        return f"[Could not read {filepath}: {e}]"


def _apply_patch(filepath: str, patch_str: str) -> bool:
    """Applies a unified diff patch to a file. Returns True on success."""
    try:
        import patch as patch_lib
        pset = patch_lib.fromstring(patch_str.encode())
        return pset.apply(root=os.path.dirname(os.path.abspath(filepath)))
    except Exception:
        return False


def run_agentless_loop(
    task_description: str,
    task_id: str = "agentless_task",
    mock_localise=None,
    mock_tester=None,
    stream_callback=None,
    model="deepseek-r1:7b"
) -> list[dict]:
    """
    Localise -> Repair -> Validate in 3 iterations.
    Returns list of event dicts for SSE stream.
    """
    workspace = os.path.abspath(WORKSPACE_DIR)
    repo_map = build_repo_map(workspace)
    events = []
    
    def _emit(ev):
        events.append(ev)
        if stream_callback:
            stream_callback(ev)

    # --- Iteration 1: Localise ---
    _emit({"type": "action", "iteration": 1, "action": "think", "thought": f"Locating bug in repo map using {model}...", "result": "Running _localise..."})
    
    localisation = _localise(task_description, repo_map, model_mock=mock_localise)
    msg = f"File: {localisation['file']} Lines: {localisation['start_line']}-{localisation['end_line']}"
    log_action(task_id, 1, "agentless_localise",
               msg,
               localisation["metrics"].get("completion_tokens", 0),
               localisation["metrics"].get("eval_duration", 0) // 1_000_000)

    _emit({"type": "action", "iteration": 1, "action": "agentless_localise", "thought": "Identified fault location.", "result": msg, "metrics": localisation["metrics"]})

    target_file = os.path.join(workspace, localisation["file"])
    try:
        span_code = _read_span(target_file, localisation["start_line"], localisation["end_line"])
    except Exception:
        span_code = ""

    # --- Iteration 2: Repair (Tester generates patch) ---
    _emit({"type": "action", "iteration": 2, "action": "think", "thought": "Generating patch for localized defect...", "result": "Calling diagnose_and_fix..."})
    
    fixed_code = diagnose_and_fix(
        original_code=span_code,
        error_trace=task_description,
        mock_response=mock_tester,
    )
    log_action(task_id, 2, "agentless_repair",
               f"Patch generated for {localisation['file']}", 0, 0)
               
    _emit({"type": "action", "iteration": 2, "action": "agentless_repair", "thought": "Patch generated.", "result": f"Replaced span with:\n{fixed_code[:100]}...", "metrics": {"prompt_tokens":0, "completion_tokens":0, "eval_duration":1}})

    # Write the fix
    try:
        with open(target_file, encoding="utf-8") as f:
            lines = f.readlines()
        start = localisation["start_line"] - 1
        end = localisation["end_line"]
        new_lines = lines[:start] + [fixed_code + "\n"] + lines[end:]
        with open(target_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        write_ok = True
    except Exception as e:
        write_ok = False
        log_action(task_id, 2, "agentless_repair_failed", str(e), 0, 0)

    if not write_ok:
        _emit({"type": "finish", "status": "failed", "summary": "Agentless repair: could not write fix to file."})
        return events

    # --- Iteration 3: Validate ---
    _emit({"type": "action", "iteration": 3, "action": "think", "thought": "Validating fix with pytest...", "result": "Running tests..."})
    
    res = execute_command_safely("python -m pytest --tb=short -q", task_id=task_id, iteration=3)
    passed = res["code"] == 0
    log_action(task_id, 3, "agentless_validate",
               f"Tests {'PASSED' if passed else 'FAILED'}: {res['stdout'][:200]}", 0, 0)

    _emit({"type": "action", "iteration": 3, "action": "agentless_validate", "thought": "Tests completed.", "result": res["stdout"][:500] + "\n" + res["stderr"][:500], "metrics": {"prompt_tokens":0, "completion_tokens":0, "eval_duration":res["latency_ms"]*1000000}})

    summary = (
        f"Agentless repair of '{localisation['file']}' L{localisation['start_line']}-{localisation['end_line']}. "
        f"Tests: {'passed' if passed else 'failed'}."
    )
    _emit({"type": "finish", "status": "success" if passed else "failed", "summary": summary})
    
    return events


# ---------------------------------------------------------------------------
# Task router helper — used by Flask route to choose loop type
# ---------------------------------------------------------------------------

FIX_KEYWORDS = re.compile(
    r"\b(fix|bug|error|exception|crash|fail|broken|wrong|incorrect|traceback|keyerror|typeerror|nameerror)\b",
    re.IGNORECASE
)

QUESTION_KEYWORDS = re.compile(
    r"\b(what|how|why|who|where|when|tell me|explain|summarize|describe|what is|can you)\b|\?$",
    re.IGNORECASE
)

def classify_task(task: str) -> str:
    """Returns 'fix' for narrow bug-fix tasks, 'knowledge' for Q&A, 'build' for everything else."""
    task_lower = task.lower().strip()
    if FIX_KEYWORDS.search(task_lower) and "tell me" not in task_lower and "explain" not in task_lower:
        return "fix"
    if QUESTION_KEYWORDS.search(task_lower) or task_lower.startswith(("what", "how", "why", "tell me", "explain", "summarize")):
        return "knowledge"
    return "build"
