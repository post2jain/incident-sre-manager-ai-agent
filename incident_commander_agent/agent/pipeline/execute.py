from __future__ import annotations
import re
from typing import List
from agent.llm import get_llm, LLMMessage
from agent.config import config
from agent.tools.mcp_server import MCPServer
from agent.tools.schemas import Doc
from agent.token_budget.packer import PackedDoc, pack_docs

ACTION_RE = re.compile(r"^Action:\s*([a-zA-Z_0-9]+)\((.*)\)\s*$", re.IGNORECASE | re.DOTALL)

class ExecutionResult:
    def __init__(self, final_output: str, trace: list[str]):
        self.final_output = final_output
        self.trace = trace

def call_tool(server: MCPServer, name: str, args_str: str):
    try:
        if name == "search_incident_corpus":
            m = re.findall(r'"([^"]+)"', args_str)
            topk_m = re.findall(r'top_k\s*=\s*(\d+)', args_str)
            query = m[0] if m else args_str
            top_k = int(topk_m[0]) if topk_m else 8
            return server.search_incident_corpus(query, top_k)
        if name == "query_metrics":
            m = re.findall(r'"([^"]+)"', args_str)
            promql = m[0] if m else args_str
            return server.query_metrics(promql)
        if name == "graph_query":
            m = re.findall(r'"([^"]+)"', args_str)
            depth_m = re.findall(r'depth\s*=\s*(\d+)', args_str)
            service = m[0] if m else "unknown"
            depth = int(depth_m[0]) if depth_m else 1
            return server.graph_query(service, depth)
        if name == "open_ticket":
            from agent.tools.schemas import TicketSpec
            return server.open_ticket("jira", TicketSpec(title="Auto", description="Auto", priority="High"))
        if name == "persist_episode":
            return "ok"
        if name == "list_recent_incidents":
            return server.list_recent_incidents(5)
        return f"Unknown tool {name}"
    except Exception as e:
        return f"Tool error: {e}"

def execute(plan_text: str,
            system_prompt: str,
            executor_prompt: str,
            server: MCPServer,
            retrieved_docs: List[Doc] | None = None) -> ExecutionResult:

    llm = get_llm("executor")
    messages: List[LLMMessage] = [
        LLMMessage(role="system", content=system_prompt),
        LLMMessage(role="user", content=executor_prompt),
        LLMMessage(role="assistant", content="Thought: I'll begin executing the plan.")
    ]

    if retrieved_docs:
        packed = pack_docs([PackedDoc(d.text, d.metadata) for d in retrieved_docs],
                           max_tokens=config.tokens.retrieval_budget_tokens)
        context_snippets = "\n\n".join([f"[DOC {i}] {d.text}" for i, d in enumerate(packed)])
        messages.append(LLMMessage(role="assistant", content=f"(internal) Context docs:\n{context_snippets}"))

    trace: list[str] = []
    final_output = ""
    max_steps = 20

    for _ in range(max_steps):
        output = llm.chat(messages)
        trace.append(output)

        if ("Incident Summary" in output and
            "Triage" in output and
            "Postmortem" in output):
            final_output = output
            break

        action_match = ACTION_RE.search(output)
        if not action_match:
            messages.append(LLMMessage(role="assistant", content=output))
            messages.append(LLMMessage(role="user", content="If you have enough info, produce the final outputs now."))
            continue

        tool_name, args_str = action_match.group(1), action_match.group(2)
        tool_result = call_tool(server, tool_name, args_str)

        messages.append(LLMMessage(role="assistant", content=output))
        messages.append(LLMMessage(role="user", content=f"Observation: {str(tool_result)[:2000]}"))

    if not final_output:
        final_output = trace[-1] if trace else "No output"

    return ExecutionResult(final_output=final_output, trace=trace)
