import tiktoken

def get_encoder(model: str = "gpt-4o-mini"):
    try:
        return tiktoken.encoding_for_model(model)
    except Exception:
        return tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    enc = get_encoder(model)
    return len(enc.encode(text or ""))
