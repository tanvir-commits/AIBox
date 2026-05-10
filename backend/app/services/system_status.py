from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.config import Settings
from app.db.session import get_engine
from app.providers.ollama_llm import ping_ollama

logger = logging.getLogger(__name__)


def _check_postgres(engine: Engine) -> dict[str, Any]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True, "detail": "connected"}
    except Exception as exc:  # noqa: BLE001 — surface dependency failures
        logger.warning("postgres check failed: %s", exc)
        return {"ok": False, "detail": str(exc)}


def _check_qdrant(url: str) -> dict[str, Any]:
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=url, timeout=5)
        client.get_collections()
        return {"ok": True, "detail": "reachable"}
    except Exception as exc:  # noqa: BLE001
        logger.warning("qdrant check failed: %s", exc)
        return {"ok": False, "detail": str(exc)}


def build_system_status(
    settings: Settings,
    *,
    engine: Engine | None = None,
) -> dict[str, Any]:
    eng = engine if engine is not None else get_engine()
    postgres = _check_postgres(eng)
    qdrant = _check_qdrant(settings.qdrant_url)
    deps: dict[str, Any] = {
        "postgres": postgres,
        "qdrant": qdrant,
    }
    if settings.default_llm_provider.strip().lower() == "ollama":
        deps["ollama"] = ping_ollama(settings)

    core_ok = postgres["ok"] and qdrant["ok"]
    return {
        "app": settings.app_name,
        "providers": {
            "llm": settings.default_llm_provider,
            "embedding": settings.default_embedding_provider,
        },
        "dependencies": deps,
        # Chat may fall back to extractive RAG if Ollama is down — do not flip global health.
        "healthy": core_ok,
    }
