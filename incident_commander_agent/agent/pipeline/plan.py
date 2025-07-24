from __future__ import annotations
from dataclasses import dataclass
from typing import List
from agent.llm import get_llm, LLMMessage
from agent.config import config

@dataclass
class PlanPhase:
    name: str
    max_tokens: int
    notes: str

@dataclass
class Plan:
    phases: List[PlanPhase]
    steps: List[str]
    raw_text: str

def render_planner_prompt(incident: str, system_prompt: str, planner_prompt: str) -> list[LLMMessage]:
    prompt = planner_prompt.replace("{{INCIDENT}}", incident)                           .replace("{{MAX_TOKENS}}", str(config.tokens.max_context_tokens))
    return [
        LLMMessage(role="system", content=system_prompt),
        LLMMessage(role="user", content=prompt)
    ]

def parse_plan(text: str) -> Plan:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    phases: List[PlanPhase] = []
    steps: List[str] = []
    in_steps = False
    for l in lines:
        if l[:2].isdigit() and l[1] == '.':
            in_steps = True
        if not in_steps:
            if l.startswith("|") and "Phase" not in l and "Max Tokens" not in l:
                parts = [p.strip() for p in l.strip("|").split("|")]
                if len(parts) >= 3:
                    try:
                        phases.append(PlanPhase(parts[0], int(parts[1]), parts[2]))
                    except Exception:
                        pass
        else:
            if l[0].isdigit() and "." in l:
                steps.append(l)
    return Plan(phases=phases, steps=steps, raw_text=text)

def generate_plan(incident: str, system_prompt: str, planner_prompt: str) -> Plan:
    llm = get_llm("planner")
    msgs = render_planner_prompt(incident, system_prompt, planner_prompt)
    text = llm.chat(msgs)
    return parse_plan(text)
