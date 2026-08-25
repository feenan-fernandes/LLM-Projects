"""
builder_loop.py
8-iteration state machine implementing the Section 5 Orchestrator action loop.
Handles all action tags, enforces the install_skill human-approval gate,
delegates self_heal to the Tester agent, and enforces the iter-6 partial rule.
"""
import os
import json

from backend.agents.orchestrator import call_orchestrator
from backend.agents.tester import diagnose_and_fix
from backend.agents.skill_installer import install_skill, load_skill_context
from backend.loop.action_parser import parse_action, extract_thought
from backend.loop.sandbox import execute_command_safely, SandboxViolationError
from backend.governance.logger import log_action

MAX_ITERATIONS = 25
PARTIAL_THRESHOLD = 20   # if no tests passing by this iter → flag partial


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _observation_prefix(action_type, iteration):
    return f"[iter {iteration}] {action_type.upper()} result"


def _human_approval_pending(action):
    """Returns an ArtifactCard-style dict the caller must surface to the user."""
    return {
        "requires_approval": True,
        "action_type": action["type"],
        "args": action["args"],
        "message": (
            "Human approval required before this action executes. "
            "Review in ArtifactCard and click Approve to proceed."
        ),
    }


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run_builder_loop(
    task_description,
    task_id="task_default",
    mock_responses=None,
    # Callbacks provided by the Flask route / test harness:
    approval_callback=None,   # callable(pending_dict) -> bool  (True = approved)
    stream_callback=None,     # callable(event_dict) -> None    (for SSE)
    skill_context_override=None,  # pre-loaded SKILL.md text injected at start
    model="deepseek-r1:7b"
):
    """
    Executes up to MAX_ITERATIONS of the Section 5 action loop.

    Returns:
        (success: bool, iterations: int, summary: str)
    """
    conversation = f"USER REQUEST: {task_description}\n"
    if skill_context_override:
        conversation += f"\nSKILL CONTEXT:\n{skill_context_override}\n"
    conversation += "\nWhat is your first action?"

    tests_passed = False
    final_summary = ""

    def _emit(event):
        if stream_callback:
            stream_callback(event)

    for i in range(MAX_ITERATIONS):
        iteration = i + 1
        _emit({"type": "system", "msg": f"Step {iteration}: Agent is thinking..."})

        # --- Call Orchestrator (or use mock) ---
        mock = mock_responses[i] if mock_responses and i < len(mock_responses) else None
        response_text, metrics = call_orchestrator(conversation, model=model, mock_response=mock)

        thought = extract_thought(response_text)
        action = parse_action(response_text)

        _emit({
            "type": "thought",
            "iteration": iteration,
            "thought": thought,
        })

        # --- No valid action ---
        if not action:
            # Partial check at iter 6
            if iteration >= PARTIAL_THRESHOLD and not tests_passed:
                summary = (
                    "Reached iteration 6 without passing tests and no valid action tag. "
                    "Flagging as partial."
                )
                log_action(task_id, iteration, "partial_flag", summary, 0, 0)
                _emit({"type": "action", "iteration": iteration, "action": "partial_flag", "result": summary})
                return False, iteration, summary

            obs = (
            "ERROR: No valid XML action tag found. "
            "You MUST output exactly ONE valid action tag. "
            "Do NOT just converse. Use <write_file>, <execute_bash>, <patch_file>, or <finish>.\n"
            "Example:\n<execute_bash>\n  <command>ls -la</command>\n</execute_bash>"
        )
            log_action(task_id, iteration, "invalid_xml", obs, metrics["completion_tokens"], metrics["eval_duration"] // 1_000_000)
            conversation += f"\n\nASSISTANT:\n{response_text}\n\n<observation>\n{obs}\n</observation>\n\nNext action?"
            _emit({"type": "action", "iteration": iteration, "action": "invalid_xml", "result": obs})
            continue

        action_type = action["type"]
        args = action["args"]
        observation = ""
        is_finished = False

        # ---------------------------------------------------------------
        try:
            # 1. PLAN — surface to UI, no side-effects
            if action_type == "plan":
                observation = (
                    f"Plan acknowledged.\n"
                    f"Goal: {args['goal']}\n"
                    f"Steps: {args['steps']}\n"
                    f"Acceptance: {args['acceptance_criteria']}\n\n"
                    f"IMPORTANT: Plan is stored in memory. DO NOT output <plan> again. You must now take the FIRST action using <write_file> or <execute_bash>."
                )

            # 2. SEARCH GITHUB SKILLS — read-only, no approval needed
            elif action_type == "search_github_skills":
                from backend.agents.skill_scout import search_skills
                results = search_skills(
                    args["query"],
                    max_candidates=5,
                )
                if results:
                    names = [r["full_name"] for r in results]
                    observation = f"Found {len(results)} candidate skill(s): {names}"
                else:
                    observation = "No candidate skills found matching query."
                _emit({"type": "skill_discovery", "candidates": results if results else []})

            # 3. EVALUATE SKILL — Librarian grades one repo
            elif action_type == "evaluate_skill":
                from backend.agents.librarian import grade_skill_relevance
                repo_url = args.get("repo_url", "")
                # In real flow we'd fetch SKILL.md; in loop we use repo description
                approved = grade_skill_relevance(task_description, repo_url)
                observation = f"Librarian evaluation: {'APPROVED' if approved else 'REJECTED'} — {repo_url}"

            # 4. INSTALL SKILL — REQUIRES HUMAN APPROVAL
            elif action_type == "install_skill":
                pending = _human_approval_pending(action)
                _emit({"type": "approval_required", "pending": pending})

                approved = False
                if approval_callback:
                    approved = approval_callback(pending)

                if approved:
                    # Build a minimal candidate dict from args
                    slug = args["repo_url"].rstrip("/").split("/")[-1]
                    candidate = {
                        "slug": slug,
                        "name": slug,
                        "full_name": args["repo_url"].replace("https://github.com/", ""),
                        "url": args["repo_url"],
                        "stars": 0,
                        "score": 0.0,
                        "skill_md": f"# {slug}\nInstalled from {args['repo_url']}",
                    }
                    path = install_skill(candidate, task_id=task_id, log_fn=log_action)
                    observation = f"Skill installed to {path}."
                else:
                    observation = "Skill install REJECTED by human reviewer. Skipping."
                    log_action(task_id, iteration, "install_rejected", observation, 0, 0)

            # 5. SELECT SKILL
            elif action_type == "select_skill":
                slug = args.get("skill_name", "")
                context = load_skill_context(slug)
                if context:
                    conversation += f"\n\nSELECTED SKILL CONTEXT ({slug}):\n{context}\n"
                    observation = f"Skill '{slug}' selected and context injected."
                else:
                    observation = f"Skill '{slug}' not found in registry. Has it been installed?"

            # 5.5 PATCH FILE
            elif action_type == "patch_file":
                path = args.get("path", "")
                diff_str = args.get("diff", "")
                workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workspace'))
                full_path = os.path.abspath(os.path.join(workspace_dir, path))
                try:
                    import patch as patch_lib
                    pset = patch_lib.fromstring(diff_str.encode('utf-8'))
                    success = pset.apply(root=os.path.dirname(full_path))
                    if success:
                        observation = f"Patch applied successfully to {path}"
                    else:
                        observation = f"Failed to apply patch to {path}. Context mismatch. Try <write_file> instead."
                except Exception as e:
                    observation = f"Error applying patch to {path}: {e}"

            # 6. WRITE FILE
            elif action_type == "write_file":
                path = args.get("path", "")
                content = args.get("content", "")
                
                # Enforce workspace boundary
                workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'workspace'))
                full_path = os.path.abspath(os.path.join(workspace_dir, path))
                if not full_path.startswith(workspace_dir):
                    observation = f"Sandbox violation: Cannot write outside workspace directory."
                else:
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    observation = f"File written: {path}"

            # 7. EXECUTE BASH
            elif action_type == "execute_bash":
                cmd = args.get("command", "")
                res = execute_command_safely(cmd, task_id=task_id, iteration=iteration)
                observation = f"STDOUT:\n{res['stdout']}\nSTDERR:\n{res['stderr']}\nExit: {res['code']}"

            # 8. RUN TEST (Phase 5 InspectCoder augmentation)
            elif action_type == "run_test":
                cmd = args.get("command", "")
                expect = args.get("expect", "")
                
                # Phase 5: Automatically inject --showlocals if using pytest to capture runtime variables
                if "pytest" in cmd and "--showlocals" not in cmd and "-l" not in cmd:
                    cmd += " --showlocals"
                    
                res = execute_command_safely(cmd, task_id=task_id, iteration=iteration)
                passed = res["code"] == 0
                tests_passed = tests_passed or passed
                observation = (
                    f"Test {'PASSED' if passed else 'FAILED'}.\n"
                    f"Expected: {expect}\n"
                    f"STDOUT:\n{res['stdout']}\nSTDERR:\n{res['stderr']}"
                )
                _emit({"type": "test_result", "passed": passed, "output": observation})

                # Iteration 6 partial rule
                if iteration >= PARTIAL_THRESHOLD and not tests_passed:
                    summary = (
                        "Reached iteration 6 without passing tests. "
                        "Narrowing scope and flagging partial."
                    )
                    log_action(task_id, iteration, "partial_flag", summary, 0, 0)
                    _emit({"type": "action", "iteration": iteration, "action": "partial_flag", "result": summary})
                    return False, iteration, summary

            # 9. SELF HEAL — delegate to Tester
            elif action_type == "self_heal":
                error_summary = args.get("error_summary", "")
                hypothesis = args.get("hypothesis", "")
                # Tester needs the last written file; we pass the hypothesis as context
                fixed = diagnose_and_fix(
                    original_code=hypothesis,
                    error_trace=error_summary,
                )
                observation = f"Tester self-heal response:\n{fixed}"


            # 10. FINISH
            elif action_type == "finish":
                status = args.get("status", "success")
                summary = args.get("summary", "")
                final_summary = summary
                is_finished = True
                observation = f"Finished [{status}]: {summary}"

        except SandboxViolationError as e:
            observation = str(e)
        except Exception as e:
            observation = f"System error in {action_type}: {e}"

        # --- Governance log ---
        log_action(
            task_id, iteration, action_type,
            observation[:2000],          # cap content to keep db lean
            metrics.get("completion_tokens", 0),
            metrics.get("eval_duration", 0) // 1_000_000,
        )

        _emit({
            "type": "action",
            "iteration": iteration,
            "action": action_type,
            "result": observation,
            "metrics": metrics,
        })

        if is_finished:
            success = action["args"].get("status", "success") == "success"
            return success, iteration, final_summary

        # Append observation to conversation
        conversation += (
            f"\n\nASSISTANT:\n{response_text}\n\n"
            f"<observation>\n{observation}\n</observation>\n\n"
            "Next action?"
        )

    # Iteration budget exhausted
    log_action(task_id, MAX_ITERATIONS, "timeout", "Iteration budget (8) exhausted.", 0, 0)
    return False, MAX_ITERATIONS, "Failed: iteration budget exhausted."
