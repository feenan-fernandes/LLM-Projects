import requests
import os

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
TESTER_MODEL = "qwen2.5-coder:7b"
TESTER_FALLBACK_MODEL = "deepseek-coder:7b"


def call_tester(prompt, use_fallback=False, mock_response=None):
    """
    Routes to qwen2.5-coder:7b (default) or deepseek-coder:7b (fallback).
    """
    if mock_response:
        return mock_response

    model = TESTER_FALLBACK_MODEL if use_fallback else TESTER_MODEL
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=900)
        if resp.status_code == 200:
            return resp.json().get("response", "")
    except Exception as e:
        print(f"Tester Error ({model}): {e}")
    return ""


def diagnose_and_fix(original_code, error_trace, use_fallback=False, mock_response=None):
    """
    Given broken code and its error trace, returns corrected code as a string.
    """
    prompt = (
        f"You are an elite Python debugger. The following code threw an error.\n"
        f"Fix it. Return ONLY the corrected code inside a single ```python code block.\n\n"
        f"Code:\n{original_code}\n\nError:\n{error_trace}"
    )
    response = call_tester(prompt, use_fallback=use_fallback, mock_response=mock_response)

    # Extract code block
    import re
    match = re.search(r"```python\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return original_code  # fallback: return unchanged
