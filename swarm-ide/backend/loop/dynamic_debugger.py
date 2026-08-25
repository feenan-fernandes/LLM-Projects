"""
dynamic_debugger.py - Phase 5
Implements InspectCoder (arXiv:2510.18327) dynamic self-heal for test failures.
Runs tests with a trace wrapper to capture local variables on AssertionError,
so the Tester agent receives concrete runtime state instead of just a traceback.
"""
import sys
import threading
import traceback
from typing import Any

# Global storage for the captured state during tracing
_captured_state = {}

def _trace_calls(frame, event, arg):
    if event == "exception":
        exc_type, exc_value, exc_traceback = arg
        if issubclass(exc_type, AssertionError) or issubclass(exc_type, Exception):
            # Capture local variables at the frame where the exception occurred
            # Filter out builtins and overly large objects
            locals_dict = frame.f_locals
            filtered = {}
            for k, v in locals_dict.items():
                if not k.startswith("__"):
                    # Capture a string representation, truncate if too large
                    val_str = repr(v)
                    if len(val_str) > 200:
                        val_str = val_str[:200] + " ... (truncated)"
                    filtered[k] = val_str
            
            # Identify the file and line number
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            _captured_state["locals"] = filtered
            _captured_state["file"] = filename
            _captured_state["line"] = lineno
    return _trace_calls

def run_with_inspection(target_func: callable, *args, **kwargs) -> dict:
    """
    Runs a target function with sys.settrace to capture state on exception.
    This is a simplified InspectCoder implementation for Python.
    """
    global _captured_state
    _captured_state = {}
    
    # We use threading to set trace just for the execution of target_func if needed,
    # or just set trace in the current thread.
    old_trace = sys.gettrace()
    sys.settrace(_trace_calls)
    
    error = None
    tb = None
    try:
        target_func(*args, **kwargs)
    except Exception as e:
        error = e
        tb = traceback.format_exc()
    finally:
        sys.settrace(old_trace)
        
    return {
        "error": error,
        "traceback": tb,
        "captured_locals": _captured_state.get("locals", {}),
        "file": _captured_state.get("file", ""),
        "line": _captured_state.get("line", ""),
    }
