from agent.token_budget.counter import count_tokens
from agent.token_budget.packer import pack_docs, PackedDoc

def test_count_tokens_basic():
    assert count_tokens("hello") > 0

def test_pack_docs_respects_limit():
    docs = [PackedDoc("word " * 500, {"i": 0}), PackedDoc("word " * 500, {"i": 1})]
    packed = pack_docs(docs, max_tokens=300)
    assert len(packed) >= 1
