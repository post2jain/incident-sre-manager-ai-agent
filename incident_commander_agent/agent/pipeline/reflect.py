from __future__ import annotations
from agent.llm import get_llm, LLMMessage

def reflect_and_improve(system_prompt: str, critic_prompt: str, draft: str) -> tuple[str, str]:
    critic_llm = get_llm("critic")
    critique = critic_llm.chat([
        LLMMessage(role="system", content=system_prompt),
        LLMMessage(role="user", content=f"{critic_prompt}\n\n---\nDRAFT:\n{draft}")
    ])

    # naive detection
    needs_fix = ("0/1" in critique) or any(
        part.strip().endswith("/5") and part.strip().split("/")[0].isdigit() and int(part.strip().split("/")[0]) < 3
        for part in critique.splitlines() if "/5" in part
    )
    if not needs_fix:
        return critique, draft

    executor_llm = get_llm("executor")
    improved = executor_llm.chat([
        LLMMessage(role="system", content=system_prompt),
        LLMMessage(role="user", content=(
            "Here is an incident draft and a critique of it. "
            "Produce an improved final version that addresses every critique point:\n\n"
            f"--- DRAFT ---\n{draft}\n\n--- CRITIQUE ---\n{critique}\n"
            "Return ONLY the improved final incident summary + triage + comms + postmortem."
        ))
    ])
    return critique, improved
