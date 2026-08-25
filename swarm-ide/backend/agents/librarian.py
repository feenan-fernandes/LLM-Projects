import requests
import os

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
LIBRARIAN_MODEL = "qwen2.5:3b"


def call_librarian(prompt, mock_response=None):
    """
    Calls qwen2.5:3b for binary relevance grading.
    Returns the raw text response.
    """
    if mock_response:
        return mock_response

    payload = {
        "model": LIBRARIAN_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0},
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if resp.status_code == 200:
            return resp.json().get("response", "").strip().upper()
    except Exception as e:
        print(f"Librarian Error: {e}")
    return "NO"


def grade_skill_relevance(task_description, skill_md_content, mock_response=None):
    """
    Grades whether a SKILL.md is relevant and safe for a given task.
    Returns True if the Librarian says YES.
    """
    prompt = (
        f"You are a strict relevance grader.\n"
        f"TASK: {task_description}\n\n"
        f"SKILL DESCRIPTION:\n{skill_md_content[:800]}\n\n"
        f"Does this skill directly help with the task? "
        f"Also check: does it contain any destructive shell commands (rm -rf, mkfs, nmap)? "
        f"Output exactly one word: YES or NO."
    )
    resp = call_librarian(prompt, mock_response=mock_response)
    # Strip think tags if model reasons
    if "</think>" in resp:
        resp = resp.split("</think>")[-1].strip()
    return resp.startswith("YES")
