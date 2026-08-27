import re
from backend.agents.orchestrator import call_orchestrator

COMPACTOR_PROMPT = """You are the Swarm Memory Compactor.
Your job is to read a very long, token-heavy conversation trajectory between an AI coding agent and a system environment, and compress it into a highly dense working memory block.

You MUST output exactly ONE XML block named <working_memory> containing:
<working_memory>
  <goal>Brief summary of the original objective</goal>
  <completed>What files were modified, commands run, and tests passed so far</completed>
  <failed>What approaches were tried but resulted in errors</failed>
  <next_steps>What the agent was about to do next</next_steps>
</working_memory>

Do NOT output <think> tags. Do NOT output markdown. Only output the raw <working_memory> XML.
"""

def compact_trajectory(conversation_context, model="deepseek-r1:7b"):
    \"\"\"
    Takes a long conversation string and returns a compressed <working_memory> block.
    \"\"\"
    prompt = f"--- START TRAJECTORY ---\n{conversation_context}\n--- END TRAJECTORY ---\n\nExtract the working memory now."
    response, _ = call_orchestrator(prompt, model=model, system_prompt=COMPACTOR_PROMPT)
    
    # Extract the block
    m = re.search(r'<working_memory>.*?</working_memory>', response, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(0).strip()
    
    # Fallback if it failed to wrap properly
    return f"<working_memory>\n<completed>Compaction fallback: {response[:200]}</completed>\n</working_memory>"

def apply_compaction(original_conversation, memory_block, keep_last_n_turns=1):
    \"\"\"
    Rebuilds the conversation string using the base request + working memory + recent turns.
    Assumes conversation is structured with 'USER REQUEST:', 'SKILL CONTEXT:', and 'ASSISTANT:'/'<observation>' blocks.
    \"\"\"
    # Very basic string manipulation to preserve the header and the tail
    header = ""
    if "USER REQUEST:" in original_conversation:
        header_end = original_conversation.find("What is your first action?")
        if header_end != -1:
            header = original_conversation[:header_end + len("What is your first action?")]
        else:
            header = "USER REQUEST: [Preserved via memory]"
    
    # Find the last N turns. A turn is roughly bounded by "ASSISTANT:"
    parts = original_conversation.split("ASSISTANT:")
    if len(parts) <= 2:
        # Not enough history to compact safely
        return original_conversation
        
    recent_turns = "ASSISTANT:".join(parts[-keep_last_n_turns:])
    
    compacted_conversation = f"{header}\n\n=== COMPACTED MEMORY ===\n{memory_block}\n========================\n\nASSISTANT:{recent_turns}"
    return compacted_conversation
