"""
skill_scout.py — Phase 0.2 upgrade: GitHub Token + rate-limit back-off
All other logic unchanged.
"""
import os
import re
import json
import time
import math
import datetime
import urllib.request
import urllib.error
import urllib.parse

SKILL_TOPICS = [
    "claude-skill", "agent-skill", "cursor-skill", "antigravity-skill",
]
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

_rate_limit_reset = 0  # epoch seconds when rate limit resets


def _gh_headers():
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def _get(url, timeout=10, retries=3) -> dict | None:
    global _rate_limit_reset
    for attempt in range(retries):
        # Honour rate limit reset if we've been throttled
        wait = _rate_limit_reset - time.time()
        if wait > 0:
            time.sleep(min(wait + 1, 60))

        req = urllib.request.Request(url, headers=_gh_headers())
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                reset_ts = e.headers.get("X-RateLimit-Reset", "")
                if reset_ts:
                    _rate_limit_reset = int(reset_ts)
                backoff = (2 ** attempt) * 5
                time.sleep(backoff)
                continue
            print(f"[skill_scout] HTTP {e.code} for {url}")
            return None
        except Exception as ex:
            print(f"[skill_scout] Error: {ex}")
            return None
    return None


def _score_candidate(item) -> float:
    stars = item.get("stargazers_count", 0)
    pushed_at = item.get("pushed_at", "")
    recency_score = 0.0
    if pushed_at:
        try:
            pushed = datetime.datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            age_days = (datetime.datetime.now(datetime.timezone.utc) - pushed).days
            recency_score = max(0, 365 - age_days)
        except Exception:
            pass
    return round(math.log1p(stars) * 10 + recency_score * 0.1, 2)


def _has_valid_frontmatter(content: str) -> bool:
    if not content.startswith("---"):
        return False
    closing = content.find("---", 3)
    if closing == -1:
        return False
    fm = content[3:closing]
    return bool(re.search(r"^name\s*:", fm, re.MULTILINE)) and \
           bool(re.search(r"^description\s*:", fm, re.MULTILINE))


def _fetch_skill_md(repo_full_name: str, default_branch: str = "main") -> str | None:
    for branch in [default_branch, "main", "master"]:
        url = f"https://raw.githubusercontent.com/{repo_full_name}/{branch}/SKILL.md"
        req = urllib.request.Request(url, headers=_gh_headers())
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                return resp.read().decode(errors="replace")
        except Exception:
            continue
    return None


def search_skills(task_description: str, max_candidates: int = 5, mock_results=None) -> list[dict]:
    """
    Searches GitHub for SKILL.md packages matching the task.
    Returns scored, Librarian-ready candidate dicts.
    Performs NO disk writes.
    """
    if mock_results is not None:
        return mock_results

    candidates: dict[str, dict] = {}

    def _add(item, repo=None):
        r = repo or item
        slug = r.get("full_name", "").replace("/", "--")
        if slug and slug not in candidates:
            candidates[slug] = {
                "slug": slug,
                "name": r.get("name", ""),
                "full_name": r.get("full_name", ""),
                "description": r.get("description", ""),
                "stars": r.get("stargazers_count", 0),
                "url": r.get("html_url", ""),
                "pushed_at": r.get("pushed_at", ""),
                "default_branch": r.get("default_branch", "main"),
                "score": _score_candidate(r),
                "skill_md": None,
                "has_valid_frontmatter": False,
                "librarian_approved": False,
            }

    # Strategy 1: topic search
    for topic in SKILL_TOPICS:
        url = f"{GITHUB_API_BASE}/search/repositories?q=topic:{topic}&sort=stars&order=desc&per_page=10"
        data = _get(url)
        if data:
            for item in data.get("items", []):
                _add(item)
        time.sleep(0.3)

    # Strategy 2: code search for SKILL.md files
    code_data = _get(f"{GITHUB_API_BASE}/search/code?q=filename:SKILL.md&sort=indexed&per_page=15")
    if code_data:
        for item in code_data.get("items", []):
            _add(item, repo=item.get("repository", {}))

    # Sort, fetch SKILL.md for top candidates
    sorted_cands = sorted(candidates.values(), key=lambda x: x["score"], reverse=True)
    top = sorted_cands[:max_candidates * 2]

    for c in top:
        md = _fetch_skill_md(c["full_name"], c.get("default_branch", "main"))
        if md:
            c["skill_md"] = md
            c["has_valid_frontmatter"] = _has_valid_frontmatter(md)

    with_fm = [c for c in top if c["has_valid_frontmatter"]]
    return with_fm[:max_candidates]


def grade_candidates(
    task_description: str,
    candidates: list[dict],
    librarian_grade_fn,
    mock_grades=None,
) -> list[dict]:
    approved = []
    for i, c in enumerate(candidates):
        flag = mock_grades[i] if mock_grades is not None and i < len(mock_grades) \
               else librarian_grade_fn(task_description, c.get("skill_md") or c.get("description", ""))
        c["librarian_approved"] = flag
        if flag:
            approved.append(c)
    return approved
