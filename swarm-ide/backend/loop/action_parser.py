"""
action_parser.py — Updated with <patch_file> tag (Phase 6)
All 11 action tags from Section 5 + patch_file.
"""
import re


def _extract(text, tag, flags=re.DOTALL):
    m = re.search(rf'<{tag}>(.*?)</{tag}>', text, flags)
    return m.group(1).strip() if m else None


def _extract_attr(text, tag, attr):
    m = re.search(rf'<{tag}\s+{attr}=["\']([^"\']*)["\']', text)
    return m.group(1).strip() if m else None


def extract_thought(xml_text):
    return _extract(xml_text, "think") or ""


def parse_action(xml_text):
    """
    Returns {"type": str, "args": dict} for the first valid action tag found, or None.
    Handles all Section 5 tags plus <patch_file>.
    """

    if "<plan>" in xml_text:
        return {"type": "plan", "args": {
            "goal": _extract(xml_text, "goal") or "",
            "steps": _extract(xml_text, "steps") or "",
            "acceptance_criteria": _extract(xml_text, "acceptance_criteria") or "",
        }}

    if "<search_github_skills>" in xml_text:
        return {"type": "search_github_skills", "args": {
            "query": _extract(xml_text, "query") or "",
            "topics": _extract(xml_text, "topics") or "",
            "min_stars": int(_extract(xml_text, "min_stars") or 0),
        }}

    if "<evaluate_skill>" in xml_text:
        return {"type": "evaluate_skill", "args": {
            "repo_url": _extract(xml_text, "repo_url") or "",
        }}

    if "<install_skill>" in xml_text:
        return {"type": "install_skill", "args": {
            "repo_url": _extract(xml_text, "repo_url") or "",
            "target_path": _extract(xml_text, "target_path") or "",
        }}

    if "<select_skill>" in xml_text:
        return {"type": "select_skill", "args": {
            "skill_name": _extract(xml_text, "skill_name") or "",
            "reason": _extract(xml_text, "reason") or "",
        }}

    if "<patch_file>" in xml_text:
        return {"type": "patch_file", "args": {
            "path": _extract(xml_text, "path") or "",
            "diff": _extract(xml_text, "diff") or "",
        }}

    if "<write_file" in xml_text:
        path = _extract(xml_text, "path") or _extract_attr(xml_text, "write_file", "path") or ""
        content = _extract(xml_text, "content") or _extract_attr(xml_text, "write_file", "content") or ""
        if not content:
            # Maybe the content is just inside the write_file tags?
            m = re.search(r'<write_file[^>]*>(.*?)</write_file>', xml_text, re.DOTALL)
            if m and not "<path>" in m.group(1):
                content = m.group(1).strip()
        return {"type": "write_file", "args": {
            "path": path,
            "content": content,
        }}

    if "<execute_bash" in xml_text:
        cmd = _extract(xml_text, "command") or _extract(xml_text, "cmd") or _extract_attr(xml_text, "execute_bash", "command") or ""
        if not cmd:
            m = re.search(r'<execute_bash[^>]*>(.*?)</execute_bash>', xml_text, re.DOTALL)
            if m: cmd = m.group(1).strip()
        return {"type": "execute_bash", "args": {"command": cmd}}

    if "<run_test>" in xml_text:
        cmd = _extract(xml_text, "command") or _extract(xml_text, "cmd") or ""
        return {"type": "run_test", "args": {
            "command": cmd,
            "expect": _extract(xml_text, "expect") or "",
        }}

    if "<self_heal>" in xml_text:
        return {"type": "self_heal", "args": {
            "error_summary": _extract(xml_text, "error_summary") or "",
            "hypothesis": _extract(xml_text, "hypothesis") or "",
        }}

    if "<finish" in xml_text:
        status = (
            _extract_attr(xml_text, "finish", "status")
            or _extract(xml_text, "status")
            or "success"
        )
        summary = _extract(xml_text, "summary") or ""
        if not summary:
            m = re.search(r'<finish[^>]*>(.*?)</finish>', xml_text, re.DOTALL)
            summary = m.group(1).strip() if m else ""
        return {"type": "finish", "args": {"status": status, "summary": summary}}

    return None
