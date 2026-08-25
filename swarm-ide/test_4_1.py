import os
import sqlite3
import sys

# Ensure import path works from swarm-ide
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.loop.sandbox import execute_command_safely, SandboxViolationError
from backend.governance.logger import DB_PATH

def test_governance_and_sandbox():
    print("Testing Sandbox Blocklist...")
    
    # 1. Test Blocklist
    try:
        execute_command_safely("rm -rf /", task_id="test_123", iteration=1)
        print("FAIL: Sandbox failed to block 'rm -rf /'")
        return False
    except SandboxViolationError as e:
        print("SUCCESS: Sandbox blocked destructive command.")
        
    # 2. Test Governance Logging
    print("Testing Governance DB Log...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT task_id, action_type, content FROM trajectory WHERE task_id = 'test_123'")
    rows = c.fetchall()
    conn.close()
    
    if len(rows) > 0 and rows[0][1] == "sandbox_violation":
        print(f"SUCCESS: Trajectory logged to governance.db -> {rows[0]}")
        return True
    else:
        print("FAIL: Trajectory was not logged correctly.")
        return False

if __name__ == "__main__":
    success = test_governance_and_sandbox()
    sys.exit(0 if success else 1)
