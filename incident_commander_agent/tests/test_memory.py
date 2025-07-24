from agent.memory.episodic import ConversationBuffer

def test_conversation_summary_trigger():
    buf = ConversationBuffer()
    for i in range(20):
        buf.add_turn("user", "hello " * 200)
    ctx = buf.assemble_context()
    assert "[WORKING SUMMARY]" in ctx
