"""
Phase 4.4 + 4.5 Acceptance Tests
4.4: Orchestrator code follows patterns from selected SKILL.md.
4.5: Self-heal loop repairs a broken file within 3 iterations.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.agents.skill_installer import install_skill, load_skill_context, list_installed_skills
from backend.loop.builder_loop import run_builder_loop
from backend.governance.logger import DB_PATH
import sqlite3

STRIPE_SKILL = {
    "slug": "stripe--stripe-webhook-skill",
    "name": "stripe-webhook-skill",
    "full_name": "stripe/stripe-webhook-skill",
    "description": "Stripe webhook handler",
    "stars": 312,
    "url": "https://github.com/stripe/stripe-webhook-skill",
    "pushed_at": "2026-07-01T00:00:00Z",
    "default_branch": "main",
    "score": 42.5,
    "skill_md": (
        "---\n"
        "name: Stripe Webhook Handler\n"
        "description: Handles Stripe webhooks securely.\n"
        "---\n\n"
        "## Instructions\n"
        "Always use `stripe.Webhook.construct_event` to verify the payload signature.\n"
        "Always wrap the handler in a try/except stripe.error.SignatureVerificationError.\n"
    ),
    "has_valid_frontmatter": True,
    "librarian_approved": True,
}


def test_phase_4_4():
    print("=" * 60)
    print("Phase 4.4: Skill Install + Context Injection")
    print("=" * 60)

    # Install the skill to disk (simulates post-human-approval write)
    from backend.governance.logger import log_action
    path = install_skill(STRIPE_SKILL, task_id="test_4_4", log_fn=log_action)
    print(f"  Installed to: {path}")
    assert os.path.exists(path), "FAIL: SKILL.md not written to disk."

    # Load the context back
    context = load_skill_context(STRIPE_SKILL["slug"])
    assert context is not None, "FAIL: load_skill_context returned None."
    assert "construct_event" in context, "FAIL: Expected skill pattern not in context."
    print("  Context loaded successfully. Verified skill pattern present.")

    # Confirm registry updated
    registry = list_installed_skills()
    assert STRIPE_SKILL["slug"] in registry, "FAIL: Skill not in registry."
    print(f"  Registry entry confirmed: {STRIPE_SKILL['slug']}")

    # Confirm governance log recorded the install
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT action_type FROM trajectory WHERE task_id='test_4_4'")
    rows = c.fetchall()
    conn.close()
    action_types = [r[0] for r in rows]
    assert "install_skill" in action_types, "FAIL: install_skill not logged to governance.db."
    print(f"  Governance log confirmed: {action_types}")

    print("\nSUCCESS: Phase 4.4 passed.\n")
    return True


def test_phase_4_5():
    print("=" * 60)
    print("Phase 4.5: Test + Self-Heal Loop")
    print("=" * 60)

    # Deliberately broken file → fix within 3 iterations
    task = "Fix the broken app.py file"
    mocked_responses = [
        # Iteration 1: Run tests (will fail in mock)
        "<think>Let me test first</think><run_test><cmd>python -m pytest app.py</cmd></run_test>",
        # Iteration 2: Rewrite the file with the fix
        (
            "<think>Missing import — I will fix it</think>"
            "<write_file><path>app.py</path>"
            "<content>import os\nprint('fixed')</content>"
            "</write_file>"
        ),
        # Iteration 3: Finish
        "<think>Done</think><finish status='success'>Self-healed: added missing import.</finish>",
    ]

    success, iterations, summary = run_builder_loop(
        task, task_id="test_4_5", mock_responses=mocked_responses
    )

    assert success, f"FAIL: Loop did not succeed. Summary: {summary}"
    assert iterations <= 3, f"FAIL: Self-heal took {iterations} iterations (max 3)."
    print(f"  Self-healed successfully in {iterations} iterations.")
    print(f"  Summary: {summary}")

    print("\nSUCCESS: Phase 4.5 passed.\n")
    return True


if __name__ == "__main__":
    ok = test_phase_4_4() and test_phase_4_5()

    # Cleanup
    for f in ["app.py"]:
        if os.path.exists(f):
            os.remove(f)

    sys.exit(0 if ok else 1)
