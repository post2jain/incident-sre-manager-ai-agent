import os
from fastapi.testclient import TestClient
from agent.tools.mcp_api import app

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_search():
    client = TestClient(app)
    r = client.post("/search", json={"query": "foo", "top_k": 2})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
