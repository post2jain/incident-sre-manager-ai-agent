# Incident Commander Agent

A production-grade, solo-buildable **SRE “Incident Commander” Agent**:
- **MCP server & tools** (metrics, vector search, graph, tickets, episodic memory)
- **Vector DB** (Qdrant or in-memory fallback)
- **Prompt-engineered Planner → Executor (ReAct) → Critic loop**
- **Strict token budgeting with `tiktoken`**
- **3-tier memory** (short-term sliding window, working summary, long-term semantic / episodic)
- **Observability** (JSON logs, OpenTelemetry spans, cost estimator)
- **Replayable evaluation harness & tests**

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export OPENAI_API_KEY=sk-...
python scripts/ingest_vector_db.py
python scripts/replay_scenarios.py --scenario data_fixtures/scenarios/kafka_hot_partition.yaml
```

Vector DB defaults to **in-memory**. To switch to **Qdrant**, set `VECTOR_BACKEND=qdrant` and run a Qdrant instance.

Open the FastAPI MCP at:
```bash
uvicorn agent.tools.mcp_api:app --host 0.0.0.0 --port 8000
```
