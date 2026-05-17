from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.core.config import Settings, get_settings
from app.models.user import User
from app.providers.ollama_llm import fetch_ollama_tags
from app.schemas.ollama_models import OllamaModelRow, OllamaModelsResponse

router = APIRouter(prefix="/api/models", tags=["models"])


def _normalize_tags(payload: dict[str, Any]) -> list[OllamaModelRow]:
    rows: list[OllamaModelRow] = []
    for raw in payload.get("models") or []:
        if not isinstance(raw, dict):
            continue
        name = raw.get("name") or raw.get("model")
        if not isinstance(name, str) or not name.strip():
            continue
        size = raw.get("size")
        mod = raw.get("modified_at")
        rows.append(
            OllamaModelRow(
                name=name.strip(),
                size=int(size) if isinstance(size, (int, float)) else None,
                modified_at=str(mod) if mod is not None else None,
            )
        )
    return rows


@router.get("/ollama", response_model=OllamaModelsResponse)
def list_ollama_models(
    _user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> OllamaModelsResponse:
    """
    List models reported by the host Ollama instance (read-only).
    Changing the default model is done via OLLAMA_MODEL / restart (Phase 5 MVP).
    """
    if settings.default_llm_provider.strip().lower() != "ollama":
        return OllamaModelsResponse(
            ollama_base_url=settings.ollama_base_url,
            configured_model=settings.ollama_model,
            default_llm_provider=settings.default_llm_provider,
            reachable=False,
            detail="DEFAULT_LLM_PROVIDER is not ollama — chat does not call this Ollama server.",
            models=[],
        )
    try:
        payload = fetch_ollama_tags(settings)
        models = _normalize_tags(payload)
        return OllamaModelsResponse(
            ollama_base_url=settings.ollama_base_url,
            configured_model=settings.ollama_model,
            default_llm_provider=settings.default_llm_provider,
            reachable=True,
            detail=None,
            models=models,
        )
    except Exception as exc:  # noqa: BLE001
        return OllamaModelsResponse(
            ollama_base_url=settings.ollama_base_url,
            configured_model=settings.ollama_model,
            default_llm_provider=settings.default_llm_provider,
            reachable=False,
            detail=str(exc)[:500],
            models=[],
        )
