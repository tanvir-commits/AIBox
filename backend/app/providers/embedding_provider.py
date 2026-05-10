"""Resolve mock vs real embedding backends from Settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import Settings

from app.providers.fastembed_embedding import FastEmbedEmbeddingProvider
from app.providers.mock_embedding import MockEmbeddingProvider


def get_embedding_provider(settings: "Settings"):  # noqa: UP037
    key = settings.default_embedding_provider.strip().lower()
    if key in ("mock_embedding", "mock"):
        return MockEmbeddingProvider()

    if key in ("fastembed", "sentence_transformers", "minilm"):
        return FastEmbedEmbeddingProvider(
            settings.embedding_model_name,
            dimensions=settings.embedding_vector_size,
        )

    raise ValueError(
        f"Unknown embedding provider '{settings.default_embedding_provider}'. "
        "Use mock_embedding or fastembed.",
    )


def embedding_provider_summary(settings: "Settings") -> str:  # noqa: UP037
    """Label for dashboards (mirrors backend config)."""
    return settings.default_embedding_provider.strip().lower()
