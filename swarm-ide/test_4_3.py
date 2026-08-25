"""
Phase 4.3 Acceptance Test
Criteria: Given a task like "build a Stripe webhook handler",
the scout surfaces at least one plausible candidate skill
OR explicitly reports none found.
Uses fully mocked GitHub + Librarian calls — no real network traffic.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.agents.skill_scout import search_skills, grade_candidates


MOCK_CANDIDATES = [
    {
        "slug": "stripe--stripe-webhook-skill",
        "name": "stripe-webhook-skill",
        "full_name": "stripe/stripe-webhook-skill",
        "description": "A SKILL.md package for handling Stripe webhooks in Python Flask.",
        "stars": 312,
        "url": "https://github.com/stripe/stripe-webhook-skill",
        "pushed_at": "2026-07-01T00:00:00Z",
        "default_branch": "main",
        "score": 42.5,
        "skill_md": (
            "---\n"
            "name: Stripe Webhook Handler\n"
            "description: Handles Stripe webhook events securely using Flask and signature verification.\n"
            "---\n\n"
            "## Instructions\nUse `stripe.Webhook.construct_event` to verify payloads.\n"
        ),
        "has_valid_frontmatter": True,
        "librarian_approved": False,
    },
    {
        "slug": "acme--payment-noop-skill",
        "name": "payment-noop-skill",
        "full_name": "acme/payment-noop-skill",
        "description": "A generic template skill unrelated to webhooks.",
        "stars": 4,
        "url": "https://github.com/acme/payment-noop-skill",
        "pushed_at": "2024-01-01T00:00:00Z",
        "default_branch": "main",
        "score": 2.1,
        "skill_md": (
            "---\n"
            "name: Payment Noop\n"
            "description: An unrelated skill for testing.\n"
            "---\n\n"
            "## Instructions\nDo nothing.\n"
        ),
        "has_valid_frontmatter": True,
        "librarian_approved": False,
    },
]


def test_skill_scout():
    print("=" * 60)
    print("Phase 4.3 Acceptance Test: GitHub Skill Discovery")
    print("=" * 60)

    task = "build a Stripe webhook handler"

    # --- Discovery (fully mocked, no network) ---
    print(f"\n[1] Searching for skills matching: '{task}'")
    candidates = search_skills(task, mock_results=MOCK_CANDIDATES)
    print(f"    Found {len(candidates)} candidate(s).")
    for c in candidates:
        print(f"    - [{c['stars']}*] {c['full_name']} | score={c['score']}")

    assert len(candidates) > 0, "FAIL: No candidates returned."

    # --- Librarian grading (fully mocked) ---
    print("\n[2] Librarian grading each candidate...")
    # Stripe skill → YES, noop skill → NO
    mock_grades = [True, False]
    approved = grade_candidates(
        task,
        candidates,
        librarian_grade_fn=None,
        mock_grades=mock_grades,
    )
    print(f"    Approved after Librarian grading: {len(approved)} candidate(s).")
    for c in approved:
        print(f"    [OK] APPROVED: {c['full_name']}")

    # Acceptance criterion: at least one approved, or explicitly report none
    if len(approved) >= 1:
        print(f"\nSUCCESS: {len(approved)} relevant skill(s) surfaced for task.")
        print("    [CHECKPOINT] Human checkpoint: ArtifactCard shown. Awaiting install approval.")
        return True
    else:
        print("\nREPORT: No relevant skills found for this task (explicit none).")
        return True  # still passes — explicit reporting counts as success


if __name__ == "__main__":
    ok = test_skill_scout()
    sys.exit(0 if ok else 1)
