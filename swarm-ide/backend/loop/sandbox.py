import os
import re
import shutil
import subprocess
import tempfile
import time
import platform

from backend.governance.logger import log_action

# Ensure docker is in PATH if installed in AppData
DOCKER_APP_DATA = os.path.expandvars(r"%LOCALAPPDATA%\Programs\DockerDesktop\resources\bin")
DOCKER_PROG_FILES = r"C:\Program Files\Docker\Docker\resources\bin"
if os.path.exists(DOCKER_APP_DATA) and DOCKER_APP_DATA not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + DOCKER_APP_DATA
if os.path.exists(DOCKER_PROG_FILES) and DOCKER_PROG_FILES not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + DOCKER_PROG_FILES

BLOCKLIST_PATTERNS = [
    r"rm\s+-rf",
    r"mkfs",
    r"nmap",
    r"curl\s+.*\|\s*sh",
    r"wget\s+.*\|\s*sh",
    r"format\s+[a-z]:",
    r"del\s+/[sq]",
    r"shutdown",
    r"reg\s+delete",
    r":(){:|:&};:",
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
    try:
        snap = tempfile.mkdtemp(prefix="swarm_snap_")
        if os.path.isdir(workspace):
            shutil.copytree(workspace, os.path.join(snap, "workspace"))
        return snap
    except Exception:
        return None

def _restore_snapshot(snapshot: str, workspace: str):
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

def _is_docker_available() -> bool:
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        return res.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def execute_command_safely(
    cmd: str,
    task_id: str = "system",
    iteration: int = 0,
    cwd: str = None,
    timeout: int = 30,
    rollback_on_failure: bool = False,
) -> dict:
    try:
        _check_blocklist(cmd)
    except SandboxViolationError as e:
        msg = str(e)
        log_action(task_id, iteration, "sandbox_violation", msg, tokens=0, latency_ms=0)
        raise

    workspace = os.path.abspath(cwd or WORKSPACE_DIR)
    run_cwd = workspace if os.path.isdir(workspace) else os.getcwd()

    snapshot = _snapshot_workspace(run_cwd) if rollback_on_failure else None

    t0 = time.monotonic()
    try:
        if _is_docker_available():
            mapped_path = run_cwd.replace('\\\\', '/')
            if mapped_path.startswith('C:'):
                mapped_path = '/c' + mapped_path[2:]
            elif mapped_path.startswith('c:'):
                mapped_path = '/c' + mapped_path[2:]
                
            docker_cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", "1g",
                "--cpus", "1.0",
                "-v", f"{run_cwd}:/workspace",
                "-w", "/workspace",
                "python:3.11-slim",
                "bash", "-c", cmd
            ]
            
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        else:
            raise SandboxViolationError("CRITICAL: Docker is not available. Native host execution is disabled for security to prevent RCE. Please start Docker Desktop.")
            
        latency_ms = int((time.monotonic() - t0) * 1000)
        success = result.returncode == 0
        rolled_back = False

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
