from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import tiktoken
from openai import OpenAI
from agent.config import config

@dataclass
class LLMMessage:
    role: Literal["system", "user", "assistant"]
    content: str

class LLM:
    def __init__(self, model: str, temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=config.llm.openai_api_key or None)

    def chat(self, messages: list[LLMMessage]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return resp.choices[0].message.content or ""

    def count_tokens(self, text: str, model_for_tiktoken: str = "gpt-4o-mini") -> int:
        try:
            enc = tiktoken.encoding_for_model(model_for_tiktoken)
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text or ""))

def get_llm(role: Literal["planner", "executor", "critic"]) -> LLM:
    if role == "planner":
        return LLM(config.llm.model_planner, config.llm.temperature)
    if role == "executor":
        return LLM(config.llm.model_executor, config.llm.temperature)
    return LLM(config.llm.model_critic, config.llm.temperature)
