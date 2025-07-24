from __future__ import annotations
from typing import List
from agent.token_budget.counter import count_tokens
from agent.memory.summarizer import summarize_text

class PackedDoc:
    def __init__(self, text: str, metadata: dict):
        self.text = text
        self.metadata = metadata

def pack_docs(docs: List[PackedDoc], max_tokens: int, model: str = "gpt-4o-mini") -> List[PackedDoc]:
    out = []
    used = 0
    for d in docs:
        t = count_tokens(d.text, model)
        if used + t <= max_tokens:
            out.append(d)
            used += t
        else:
            remaining = max_tokens - used
            if remaining <= 0:
                break
            compressed = summarize_text(d.text, target_tokens=remaining)
            if count_tokens(compressed, model) <= remaining and compressed.strip():
                out.append(PackedDoc(text=compressed, metadata=d.metadata))
                used += count_tokens(compressed, model)
            break
    return out
