from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from agent.config import config
from agent.embeddings import embed_one

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except Exception:
    QDRANT_AVAILABLE = False

@dataclass
class VectorDoc:
    id: str
    text: str
    metadata: dict
    vector: np.ndarray

def cosine(u: np.ndarray, v: np.ndarray) -> float:
    denom = (np.linalg.norm(u) * np.linalg.norm(v)) or 1e-9
    return float(np.dot(u, v) / denom)

class InMemoryVectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.docs: List[VectorDoc] = []

    def upsert(self, docs: List[VectorDoc]):
        self.docs.extend(docs)

    def search(self, query_vec: np.ndarray, top_k: int, metadata_filter: Optional[dict] = None):
        scored = []
        for d in self.docs:
            if metadata_filter:
                ok = all(d.metadata.get(k) == v for k, v in metadata_filter.items())
                if not ok:
                    continue
            sim = cosine(query_vec, d.vector)
            scored.append((sim, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

class VectorIndex:
    def __init__(self):
        self.backend = config.vector.backend
        self.dim = config.vector.embedding_dim
        if self.backend == "qdrant" and QDRANT_AVAILABLE:
            self._qdrant = QdrantClient(url=config.vector.qdrant_url)
            try:
                self._qdrant.get_collection(config.vector.collection_name)
            except Exception:
                self._qdrant.recreate_collection(
                    config.vector.collection_name,
                    vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE),
                )
            self._mem = None
        else:
            self._qdrant = None
            self._mem = InMemoryVectorStore(dim=self.dim)

    def upsert(self, docs: List[VectorDoc]):
        if self._qdrant:
            points = [
                PointStruct(
                    id=d.id,
                    vector=d.vector.tolist(),
                    payload={**d.metadata, "text": d.text},
                )
                for d in docs
            ]
            self._qdrant.upsert(collection_name=config.vector.collection_name, points=points)
        else:
            self._mem.upsert(docs)

    def search(self, query_vec: np.ndarray, top_k: int, metadata_filter: Optional[dict] = None):
        if self._qdrant:
            flt = None
            if metadata_filter:
                must = [FieldCondition(key=k, match=MatchValue(value=v)) for k, v in metadata_filter.items()]
                flt = Filter(must=must)
            result = self._qdrant.search(
                collection_name=config.vector.collection_name,
                query_vector=query_vec.tolist(),
                limit=top_k,
                query_filter=flt
            )
            out = []
            for r in result:
                payload = r.payload or {}
                text = payload.pop("text", "")
                out.append((r.score, VectorDoc(id=str(r.id), text=text, metadata=payload, vector=np.zeros(self.dim))))
            return out
        else:
            return self._mem.search(query_vec, top_k, metadata_filter)

def mmr(query_vec: np.ndarray, candidates, k_diverse: int, lambda_mult: float = 0.7):
    # fallback: top k_diverse
    return [c[1] for c in candidates[:k_diverse]]

def embed_query(text: str) -> np.ndarray:
    return embed_one(text)
