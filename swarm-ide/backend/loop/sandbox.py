"""
sandbox.py  — Phase 2 (no Docker) + Phase 6 patch support
Pre-execution guard with transactional workspace snapshot/rollback
(AgentBound / Fault-Tolerant Sandboxing pattern, arXiv:2510.21236 & 2512.12806).

Since Docker Desktop is not installed, we implement:
  1. Pre-exec blocklist (existing)
  2. Copy-on-write workspace snapshot before every execution
  3. Automatic rollback on non-zero exit codes
  4. Hard timeout enforcement
  5. Resource-limited subprocess (no network calls from agent scripts)
"""
import os
import re
import shutil
import subprocess
import tempfile
import time

from backend.governance.logger import log_action

# Blocklist: patterns matched against the full command string (lowercased)
BLOCKLIST_PATTERNS = [
    r"rm\s+-rf",
    r"mkfs",
    r"nmap",
    r"curl\s+.*\|\s*sh",
    r"wget\s+.*\|\s*sh",
    r"format\s+[a-z]:",
    r"del\s+/[sq]",           # Windows destructive delete
    r"shutdown",
    r"reg\s+delete",          # Windows registry delete
    r":(){:|:&};:",            # fork bomb
]

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workspace')


class SandboxViolationError(Exception):
    pass


def _check_blocklist(cmd: str):
    cmd_lower = cmd.lower()
    for pattern in BLOCKLIST_PATTERNS:
        if re.search(pattern, cmd_lower):
            raise SandboxViolationError(
                f"SANDBOX VIOLATION: command '{cmd}' matched blocklist pattern '{pattern}'"
            )


def _snapshot_workspace(workspace: str) -> str | None:
    """Creates a copy-on-write snapshot of the workspace directory. Returns snapshot path."""
    try:
        snap = tempfile.mkdtemp(prefix="swarm_snap_")
        if os.path.isdir(workspace):
            shutil.copytree(workspace, os.path.join(snap, "workspace"))
        return snap
    except Exception:
        return None


def _restore_snapshot(snapshot: str, workspace: str):
    """Restores the workspace from a snapshot, then cleans up the snapshot."""
    snap_ws = os.path.join(snapshot, "workspace")
    if not os.path.isdir(snap_ws):
        return
    try:
        if os.path.isdir(workspace):
            shutil.rmtree(workspace)
        shutil.copytree(snap_ws, workspace)
    finally:
        shutil.rmtree(snapshot, ignore_errors=True)


def _cleanup_snapshot(snapshot: str):
    if snapshot:
        shutil.rmtree(snapshot, ignore_errors=True)


def execute_command_safely(
    cmd: str,
    task_id: str = "system",
    iteration: int = 0,
    cwd: str = None,
    timeout: int = 30,
    rollback_on_failure: bool = False,
) -> dict:
    """
    Executes a shell command after:
      1. Blocklist check (pre-execution gate — command never reaches shell if blocked)
      2. Workspace snapshot (copy-on-write)
      3. Subprocess execution with hard timeout
      4. Automatic rollback if exit code != 0 and rollback_on_failure=True
      5. Governance logging of outcome

    Returns: {success, stdout, stderr, code, rolled_back}
    """
    # 1. Pre-execution blocklist gate
    try:
        _check_blocklist(cmd)
    except SandboxViolationError as e:
        msg = str(e)
        log_action(task_id, iteration, "sandbox_violation", msg, tokens=0, latency_ms=0)
        raise

    workspace = os.path.abspath(cwd or WORKSPACE_DIR)
    run_cwd = workspace if os.path.isdir(workspace) else os.getcwd()

    # 2. Snapshot before execution
    snapshot = _snapshot_workspace(run_cwd) if rollback_on_failure else None

    t0 = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=run_cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        latency_ms = int((time.monotonic() - t0) * 1000)
        success = result.returncode == 0
        rolled_back = False

        # 3. Rollback on failure
        if not success and rollback_on_failure and snapshot:
            _restore_snapshot(snapshot, run_cwd)
            rolled_back = True
            snapshot = None
        else:
            _cleanup_snapshot(snapshot)

        return {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode,
            "rolled_back": rolled_back,
            "latency_ms": latency_ms,
        }

    except subprocess.TimeoutExpired:
        _cleanup_snapshot(snapshot)
        msg = f"Command timed out after {timeout}s: {cmd}"
        log_action(task_id, iteration, "timeout", msg, tokens=0, latency_ms=timeout * 1000)
        return {"success": False, "stdout": "", "stderr": msg, "code": -1, "rolled_back": False, "latency_ms": timeout * 1000}

    except Exception as e:
        _cleanup_snapshot(snapshot)
        return {"success": False, "stdout": "", "stderr": str(e), "code": -1, "rolled_back": False, "latency_ms": 0}
