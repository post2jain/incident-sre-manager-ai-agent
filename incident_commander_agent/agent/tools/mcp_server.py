from __future__ import annotations
from typing import List
import os, json, time, uuid
import pandas as pd
import numpy as np
from agent.config import config
from agent.tools.schemas import (
    Doc, MetricsResult, TicketSpec, TicketResponse,
    DependencyNode, DependencySubgraph, Episode, RecentIncidents
)
from agent.memory.semantic_vector import VectorIndex, VectorDoc, mmr, embed_query
from agent.embeddings import embed_one

class MCPServer:
    def __init__(self, vector_index: VectorIndex):
        self.vector = vector_index
        self.episodes: list[Episode] = []
        self.metrics_cache: dict[str, pd.DataFrame] = {}

    def search_incident_corpus(self, query: str, top_k: int = 8) -> List[Doc]:
        q_vec = embed_query(query)
        results = self.vector.search(q_vec, top_k=config.vector.k_primary)
        selected = mmr(q_vec, results, k_diverse=config.vector.k_diverse)
        selected_ids = set(d.id for d in selected)
        docs: List[Doc] = []
        for score, d in results:
            if d.id in selected_ids:
                docs.append(Doc(id=d.id, text=d.text, score=float(score), metadata=d.metadata))
        return docs

    def query_metrics(self, promql: str) -> MetricsResult:
        metric_name = promql.split("(")[-1].split(")")[0].split("{")[0].strip().strip("}")
        df = self._load_metric(metric_name)
        values = list(zip(df["ts"].tolist(), df["value"].tolist()))
        return MetricsResult(metric=metric_name, values=values)

    def open_ticket(self, system: str, payload: TicketSpec) -> TicketResponse:
        ticket_id = f"{system.upper()}-{np.random.randint(1000, 9999)}"
        return TicketResponse(id=ticket_id, system=system)

    def graph_query(self, service: str, depth: int = 1) -> DependencySubgraph:
        with open(config.tools.graph_file, "r") as f:
            graph = json.load(f)
        visited = set()
        q = [(service, 0)]
        nodes = {}
        while q:
            cur, d = q.pop(0)
            if cur in visited or d > depth:
                continue
            visited.add(cur)
            children = graph.get(cur, [])
            nodes[cur] = DependencyNode(name=cur, children=children)
            for c in children:
                q.append((c, d+1))
        return DependencySubgraph(nodes=list(nodes.values()))

    def persist_episode(self, summary: str, embeddings: list[float] | None, tags: list[str]) -> str:
        eid = str(uuid.uuid4())
        self.episodes.append(Episode(id=eid, summary=summary, tags=tags))
        vec = np.array(embeddings, dtype=np.float32) if embeddings else embed_one(summary)
        self.vector.upsert([VectorDoc(id=eid, text=summary, metadata={"type": "episode", "tags": tags}, vector=vec)])
        return eid

    def list_recent_incidents(self, limit: int = 10) -> RecentIncidents:
        return RecentIncidents(incidents=self.episodes[-limit:])

    def _load_metric(self, metric: str) -> pd.DataFrame:
        if metric in self.metrics_cache:
            return self.metrics_cache[metric]
        path = os.path.join(config.tools.metrics_data_dir, f"{metric}.csv")
        if not os.path.exists(path):
            ts = np.arange(int(time.time()) - 3600, int(time.time()), 60)
            df = pd.DataFrame({"ts": ts, "value": np.random.rand(len(ts))})
        else:
            df = pd.read_csv(path)
        self.metrics_cache[metric] = df
        return df
