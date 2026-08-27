"""
skill_installer.py — Phase 4.4
Handles writing an approved skill to /backend/skills/{slug}/SKILL.md.
This module is ONLY called after explicit human approval via ArtifactCard.
Logs every write to governance.db.
"""
import os
import json

SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'skills')
REGISTRY_PATH = os.path.join(SKILLS_DIR, 'registry.json')


def _load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}


def _save_registry(registry):
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)


def install_skill(candidate, task_id="system", log_fn=None):
    """
    Writes an approved skill's SKILL.md to /backend/skills/{slug}/SKILL.md.
    Updates registry.json.
    Logs the write to governance.db if log_fn is provided.

    Args:
        candidate: dict from skill_scout (must have slug, skill_md, full_name, url).
        log_fn: callable(task_id, iteration, action_type, content, tokens, latency) -> bool
    Returns:
        str: path to the installed SKILL.md file.
    """
    import werkzeug.utils
    slug = werkzeug.utils.secure_filename(candidate["slug"])
    if not slug:
        raise ValueError("Invalid skill slug.")
    skill_md = candidate.get("skill_md", "")

    if not skill_md:
        raise ValueError(f"Candidate '{slug}' has no SKILL.md content to install.")

    skill_dir = os.path.join(SKILLS_DIR, slug)
    os.makedirs(skill_dir, exist_ok=True)

    skill_path = os.path.join(skill_dir, "SKILL.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(skill_md)

    # Update registry
    registry = _load_registry()
    registry[slug] = {
        "name": candidate.get("name", slug),
        "full_name": candidate.get("full_name", ""),
        "url": candidate.get("url", ""),
        "stars": candidate.get("stars", 0),
        "score": candidate.get("score", 0.0),
        "installed_path": skill_path,
    }
    _save_registry(registry)

    # Governance log
    if log_fn:
        log_fn(task_id, 0, "install_skill", f"Installed skill '{slug}' to {skill_path}", 0, 0)

    return skill_path


def load_skill_context(slug):
    """
    Reads the installed SKILL.md for a given slug and returns its content.
    Used by the Orchestrator to inject skill context into its working memory.
    """
    skill_path = os.path.join(SKILLS_DIR, slug, "SKILL.md")
    if not os.path.exists(skill_path):
        return None
    with open(skill_path, "r", encoding="utf-8") as f:
        return f.read()


def list_installed_skills():
    """Returns all currently installed skills from the registry."""
    return _load_registry()
