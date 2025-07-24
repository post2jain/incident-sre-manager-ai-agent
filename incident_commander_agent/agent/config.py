from __future__ import annotations
from pydantic import BaseModel
import os

class VectorConfig(BaseModel):
    backend: str = os.getenv("VECTOR_BACKEND", "memory")  # memory | qdrant
    collection_name: str = "incident_corpus"
    embedding_dim: int = int(os.getenv("EMBED_DIM", "1536"))
    embedding_model: str = os.getenv("EMBED_MODEL", "text-embedding-3-large")
    similarity_threshold: float = 0.78
    k_primary: int = 8
    k_diverse: int = 4
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")

class TokenConfig(BaseModel):
    max_context_tokens: int = int(os.getenv("MAX_CONTEXT", "16000"))
    retrieval_budget_tokens: int = 6000
    reasoning_budget_tokens: int = 4000
    output_budget_tokens: int = 3000
    reflection_budget_tokens: int = 1000
    short_term_window_tokens: int = 1200
    summarize_every_n_turns: int = 5

class ToolConfig(BaseModel):
    enable_run_shell: bool = os.getenv("ENABLE_RUN_SHELL", "false").lower() == "true"
    allowed_shell_cmds: set[str] = {"ls", "pwd", "whoami"}
    metrics_data_dir: str = "data_fixtures/metrics"
    graph_file: str = "data_fixtures/graphs/services.json"

class CostConfig(BaseModel):
    prompt_cost_per_1k: float = 0.003
    completion_cost_per_1k: float = 0.006

class LLMConfig(BaseModel):
    provider: str = os.getenv("LLM_PROVIDER", "openai")
    model_planner: str = os.getenv("PLANNER_MODEL", "gpt-4o-mini")
    model_executor: str = os.getenv("EXECUTOR_MODEL", "gpt-4o-mini")
    model_critic: str = os.getenv("CRITIC_MODEL", "gpt-4o-mini")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

class AppConfig(BaseModel):
    vector: VectorConfig = VectorConfig()
    tokens: TokenConfig = TokenConfig()
    tools: ToolConfig = ToolConfig()
    costs: CostConfig = CostConfig()
    llm: LLMConfig = LLMConfig()

config = AppConfig()
