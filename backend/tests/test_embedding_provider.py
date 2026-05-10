import pytest

from app.core.config import Settings
from app.providers.embedding_provider import get_embedding_provider
from app.providers.fastembed_embedding import FastEmbedEmbeddingProvider
from app.providers.mock_embedding import MockEmbeddingProvider


def test_embedding_factory_mock() -> None:
    s = Settings(default_embedding_provider="mock_embedding")
    p = get_embedding_provider(s)
    assert isinstance(p, MockEmbeddingProvider)
    assert len(p.embed("hello")) == 384


def test_embedding_factory_fastembed_aliases() -> None:
    for key in ("fastembed", "sentence_transformers", "minilm"):
        s = Settings(default_embedding_provider=key)
        p = get_embedding_provider(s)
        assert isinstance(p, FastEmbedEmbeddingProvider)
        assert p.dimensions == 384
        assert "MiniLM" in p.model_name


def test_embedding_factory_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown embedding provider"):
        get_embedding_provider(Settings(default_embedding_provider="bogus"))
