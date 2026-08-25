import os

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add thought handler in stream processing block
content = content.replace(
    \"                } else if (data.type === 'stream') {\",
    \"                } else if (data.type === 'thought') {\\n                    updateFlowState('thinking');\\n                } else if (data.type === 'stream') {\"
)

# 2. Fix the visual output format for 'action'
old_action_block = \"\"\"                } else if (data.type === 'action') {
                    updateFlowState("action");
                    setTimeout(() => updateFlowState("validate"), 1000);

                    if (data.violation) {
                        turnLog.innerHTML += <div style="color: var(--accent-red); margin-top: 10px; font-weight: bold; background: rgba(218,54,51,0.1); padding: 8px; border: 1px solid var(--accent-red); border-radius: 6px;"><i data-lucide="alert-triangle" class="lucide-sm" style="display:inline-block; vertical-align:middle; margin-right:4px;"></i> GOVERNANCE ALERT: Sandbox Safety Violation Detected. Logging Trajectory.</div>;
                    }
                    if (data.action === "Finished.") finalSummary = data.result;
                    turnLog.innerHTML += 
                    <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed var(--border);">
                        <strong style="color: var(--accent-yellow);">Iteration \:</strong><br>
                        <span style="color: var(--text-muted);">Thought:</span> \<br>
                        <strong style="color: var(--accent-blue);">Action:</strong> \<br>
                        <strong style="color: var(--accent-green);">Result:</strong> <pre style="background:var(--bg-base); padding:8px; border:1px solid var(--border); border-radius:4px; max-height:200px; overflow-y:auto; font-size:0.8rem; margin-top:5px;">\</pre>
                    </div>;\"\"\"

new_action_block = \"\"\"                } else if (data.type === 'action') {
                    updateFlowState("action");
                    if (data.action === "run_test" || data.action === "evaluate_skill") {
                        setTimeout(() => updateFlowState("validate"), 500);
                    }
                    
                    if (data.violation) {
                        turnLog.innerHTML += <div style="color: var(--accent-red); margin-top: 10px; font-weight: bold; background: rgba(218,54,51,0.1); padding: 8px; border: 1px solid var(--accent-red); border-radius: 6px;"><i data-lucide="alert-triangle" class="lucide-sm" style="display:inline-block; vertical-align:middle; margin-right:4px;"></i> GOVERNANCE ALERT: Sandbox Safety Violation Detected. Logging Trajectory.</div>;
                    }
                    if (data.action === "Finished.") finalSummary = data.result;
                    
                    let icon = "play";
                    let stepMsg = "";
                    if (data.action === "plan") { icon = "list-todo"; stepMsg = "Agent formulated a strategic plan."; }
                    else if (data.action === "write_file") { icon = "file-code"; stepMsg = "Agent modified code files."; }
                    else if (data.action === "execute_bash") { icon = "terminal"; stepMsg = "Agent executing shell commands."; }
                    else if (data.action === "run_test") { icon = "test-tube"; stepMsg = "Agent running validation tests."; }
                    else if (data.action === "patch_file") { icon = "git-commit"; stepMsg = "Agent patching source code."; }
                    else if (data.action === "self_heal") { icon = "band-aid"; stepMsg = "Agent attempting to self-heal."; }
                    else if (data.action === "search_github_skills") { icon = "search"; stepMsg = "Agent searching skill registry."; }
                    else if (data.action === "install_skill") { icon = "download"; stepMsg = "Agent downloading skill."; }
                    else if (data.action === "select_skill") { icon = "check-circle"; stepMsg = "Agent selected a skill context."; }
                    else if (data.action === "partial_flag") { icon = "flag"; stepMsg = "Agent reached iteration limits."; }
                    else if (data.action === "invalid_xml") { icon = "alert-circle"; stepMsg = "System steering agent safely."; }
                    else { icon = "check"; stepMsg = "Agent completed step."; }

                    turnLog.innerHTML += 
                    <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed var(--border);">
                        <strong style="color: var(--accent-yellow);"><i data-lucide="\" class="lucide-sm" style="display:inline-block; vertical-align:middle; margin-right:4px;"></i> Step \: \</strong>
                        <pre style="background:var(--bg-base); padding:8px; border:1px solid var(--border); border-radius:4px; max-height:200px; overflow-y:auto; font-size:0.8rem; margin-top:5px; color: var(--text-muted);">\</pre>
                    </div>;
                    if (window.lucide) window.lucide.createIcons();\"\"\"

content = content.replace(old_action_block, new_action_block)

# 3. Handle finish type updating flowchart
old_finish_block = \"\"\"                } else if (data.type === 'finish') {
                    if (data.status === "success") {
                        finalSummary = data.summary;
                    }\"\"\"

new_finish_block = \"\"\"                } else if (data.type === 'finish') {
                    updateFlowState("done");
                    if(liveTimer) clearInterval(liveTimer);
                    if (data.status === "success") {
                        finalSummary = data.summary;
                    }\"\"\"

content = content.replace(old_finish_block, new_finish_block)

# 4. Clear interval in finally block
old_finally_block = \"\"\"                .finally(() => {
                    queryInput.disabled = false;\"\"\"

new_finally_block = \"\"\"                .finally(() => {
                    if(liveTimer) clearInterval(liveTimer);
                    queryInput.disabled = false;\"\"\"

content = content.replace(old_finally_block, new_finally_block)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced successfully")
