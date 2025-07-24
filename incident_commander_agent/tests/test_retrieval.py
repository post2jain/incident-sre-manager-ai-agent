import numpy as np
from agent.memory.semantic_vector import VectorIndex, VectorDoc
from agent.config import config

def test_inmemory_search_basic():
    config.vector.backend = "memory"
    vi = VectorIndex()
    dim = config.vector.embedding_dim
    a = VectorDoc("1", "alpha doc", {"type":"runbook"}, np.ones(dim, dtype=np.float32))
    b = VectorDoc("2", "beta doc", {"type":"runbook"}, np.ones(dim, dtype=np.float32)*0.5)
    vi.upsert([a,b])
    q = np.ones(dim, dtype=np.float32)
    res = vi.search(q, top_k=2)
    assert len(res) == 2
