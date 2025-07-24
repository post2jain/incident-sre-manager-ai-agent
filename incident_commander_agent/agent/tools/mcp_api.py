from __future__ import annotations
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from agent.memory.semantic_vector import VectorIndex
from agent.tools.mcp_server import MCPServer
from agent.tools.schemas import (
    Doc, TicketSpec, TicketResponse, MetricsResult,
    DependencySubgraph, RecentIncidents
)
from agent.tools.security import verify_api_key, validate_promql

app = FastAPI(title="Incident MCP Server", version="0.1.0")

_vector: VectorIndex | None = None
_server: MCPServer | None = None

@app.on_event("startup")
def _startup():
    global _vector, _server
    _vector = VectorIndex()
    _server = MCPServer(_vector)

class SearchReq(BaseModel):
    query: str
    top_k: int = 8

class MetricsReq(BaseModel):
    promql: str

class GraphReq(BaseModel):
    service: str
    depth: int = 1

class PersistReq(BaseModel):
    summary: str
    embeddings: List[float] | None = None
    tags: List[str]

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/version")
def version():
    return {"version": app.version}

@app.post("/search", response_model=List[Doc])
def search(req: SearchReq, _=Depends(verify_api_key)):
    assert _server is not None
    return _server.search_incident_corpus(req.query, req.top_k)

@app.post("/metrics", response_model=MetricsResult)
def metrics(req: MetricsReq, _=Depends(verify_api_key)):
    assert _server is not None
    validate_promql(req.promql)
    return _server.query_metrics(req.promql)

@app.post("/graph", response_model=DependencySubgraph)
def graph(req: GraphReq, _=Depends(verify_api_key)):
    assert _server is not None
    return _server.graph_query(req.service, req.depth)

@app.post("/ticket", response_model=TicketResponse)
def ticket(spec: TicketSpec, _=Depends(verify_api_key)):
    assert _server is not None
    return _server.open_ticket("jira", spec)

@app.post("/persist")
def persist(req: PersistReq, _=Depends(verify_api_key)):
    assert _server is not None
    return {"id": _server.persist_episode(req.summary, req.embeddings, req.tags)}

@app.get("/recent", response_model=RecentIncidents)
def recent(limit: int = 10, _=Depends(verify_api_key)):
    assert _server is not None
    return _server.list_recent_incidents(limit)
