from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Literal

class Doc(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict

class MetricsResult(BaseModel):
    metric: str
    values: list[tuple[float, float]]

class TicketSpec(BaseModel):
    title: str
    description: str
    priority: Literal["Low", "Medium", "High"]

class TicketResponse(BaseModel):
    id: str
    system: Literal["jira", "linear"]

class DependencyNode(BaseModel):
    name: str
    children: list[str] = Field(default_factory=list)

class DependencySubgraph(BaseModel):
    nodes: list[DependencyNode]

class Episode(BaseModel):
    id: str
    summary: str
    tags: list[str]

class RecentIncidents(BaseModel):
    incidents: list[Episode]
