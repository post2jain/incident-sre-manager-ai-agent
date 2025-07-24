from __future__ import annotations
from agent.token_budget.counter import count_tokens

def summarize_text(text: str, target_tokens: int) -> str:
    if count_tokens(text) <= target_tokens:
        return text
    sentences = text.split(".")
    out = []
    total = 0
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        t = count_tokens(s)
        if total + t > target_tokens:
            break
        out.append(s)
        total += t
    return ". ".join(out) + "..."
