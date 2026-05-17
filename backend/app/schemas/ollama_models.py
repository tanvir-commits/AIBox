from __future__ import annotations

from pydantic import BaseModel, Field


class OllamaModelRow(BaseModel):
    name: str
    size: int | None = None
    modified_at: str | None = None


class OllamaModelsResponse(BaseModel):
    ollama_base_url: str
    configured_model: str = Field(description="OLLAMA_MODEL from server config (restart to apply changes)")
    default_llm_provider: str
    reachable: bool
    detail: str | None = None
    models: list[OllamaModelRow] = Field(default_factory=list)
