from app.providers.mock_embedding import MockEmbeddingProvider
from app.providers.mock_llm import MockLLMProvider


def test_mock_llm_deterministic() -> None:
    llm = MockLLMProvider()
    out = llm.generate("What is the emergency procedure for the office manager?")
    assert "15 minutes" in out


def test_mock_llm_not_found_tone() -> None:
    llm = MockLLMProvider()
    out = llm.generate("no context here — not found")
    assert "could not find" in out.lower()


def test_mock_embedding_deterministic() -> None:
    emb = MockEmbeddingProvider()
    a = emb.embed("hello")
    b = emb.embed("hello")
    assert len(a) == emb.dimensions
    assert a == b
    assert a != emb.embed("world")
