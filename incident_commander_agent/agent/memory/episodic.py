from __future__ import annotations
from pydantic import BaseModel
from typing import Deque
from collections import deque
from agent.config import config
from agent.memory.summarizer import summarize_text
from agent.token_budget.counter import count_tokens

class Turn(BaseModel):
    role: str
    content: str

class ConversationBuffer:
    def __init__(self):
        self.turns: Deque[Turn] = deque()
        self.summary: str = ""
        self.turns_since_summary = 0

    def add_turn(self, role: str, content: str):
        self.turns.append(Turn(role=role, content=content))
        self.turns_since_summary += 1
        self._enforce_window()

    def _enforce_window(self):
        total_tokens = sum(count_tokens(t.content) for t in self.turns)
        if (total_tokens > config.tokens.short_term_window_tokens or 
            self.turns_since_summary >= config.tokens.summarize_every_n_turns):
            self._summarize_old_turns()

    def _summarize_old_turns(self):
        if len(self.turns) <= 2:
            return
        old_text = "\n".join([f"{t.role}: {t.content}" for t in list(self.turns)[:-2]])
        new_summary = summarize_text(old_text, target_tokens=int(config.tokens.short_term_window_tokens * 0.3))
        self.summary += "\n" + new_summary if self.summary else new_summary
        last_two = list(self.turns)[-2:]
        self.turns.clear()
        for t in last_two:
            self.turns.append(t)
        self.turns_since_summary = 0

    def assemble_context(self) -> str:
        parts = []
        if self.summary:
            parts.append(f"[WORKING SUMMARY]\n{self.summary}\n")
        parts.extend([f"{t.role}: {t.content}" for t in self.turns])
        return "\n".join(parts)
