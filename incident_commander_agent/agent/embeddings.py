from __future__ import annotations
import numpy as np
from openai import OpenAI
from agent.config import config

_client: OpenAI | None = None

def _client_once() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=config.llm.openai_api_key or None)
    return _client

def embed(texts: list[str]) -> np.ndarray:
    resp = _client_once().embeddings.create(
        model=config.vector.embedding_model,
        input=texts,
    )
    vecs = [np.asarray(d.embedding, dtype=np.float32) for d in resp.data]
    return np.vstack(vecs)

def embed_one(text: str) -> np.ndarray:
    return embed([text])[0]
