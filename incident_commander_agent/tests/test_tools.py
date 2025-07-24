from agent.memory.semantic_vector import VectorIndex
from agent.tools.mcp_server import MCPServer

def test_list_recent_incidents():
    srv = MCPServer(VectorIndex())
    eid = srv.persist_episode("summary", None, ["sev1"])
    recent = srv.list_recent_incidents(5)
    assert any(e.id == eid for e in recent.incidents)
