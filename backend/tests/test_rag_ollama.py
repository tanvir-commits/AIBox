from app.services.rag import NOT_FOUND, RetrievedChunk
from app.services.rag_ollama import _drop_not_found_when_cited, ollama_rag_answer


class _FakeOllamaOK:
    def chat(self, *, system: str, user: str) -> str:
        assert "Sources:" in user
        assert "[1]" in user
        return "The device includes timers — see timing details in [1]."


class _FakeOllamaDown:
    def chat(self, *, system: str, user: str) -> str:
        raise ConnectionError("ollama unreachable")


def test_ollama_rag_answer_calls_model() -> None:
    chunks = [
        RetrievedChunk(
            score=0.2,
            chunk_id="c1",
            document_id="d1",
            filename="ref.pdf",
            chunk_index=0,
            page_number=2,
            text="The STM32F405 microcontroller includes multiple timers for PWM generation.",
        )
    ]
    reply, cites = ollama_rag_answer(
        "Does the STM32F405 mention timers?",
        chunks,
        min_overlap=1,
        ollama=_FakeOllamaOK(),
    )
    assert "timers" in reply.lower()
    assert cites and cites[0]["filename"] == "ref.pdf"


def test_ollama_rag_answer_falls_back_when_ollama_fails() -> None:
    chunks = [
        RetrievedChunk(
            score=0.2,
            chunk_id="c1",
            document_id="d1",
            filename="ref.pdf",
            chunk_index=0,
            page_number=2,
            text="The STM32F405 microcontroller includes multiple timers.",
        )
    ]
    reply, cites = ollama_rag_answer(
        "stm32f405 timers",
        chunks,
        min_overlap=1,
        ollama=_FakeOllamaDown(),
    )
    assert "Based on indexed company documents:" in reply
    assert cites and cites[0]["filename"] == "ref.pdf"


def test_ollama_rag_answer_policy_shortcut_without_llm() -> None:
    class _MustNotCall:
        def chat(self, *, system: str, user: str) -> str:
            raise AssertionError("should use policy shortcut, not LLM")

    chunks = [
        RetrievedChunk(
            score=0.9,
            chunk_id="c1",
            document_id="d1",
            filename="handbook.txt",
            chunk_index=0,
            page_number=None,
            text="The emergency contact procedure requires staff to notify the office manager within 15 minutes.",
        )
    ]
    reply, cites = ollama_rag_answer(
        "How fast do staff need to notify the office manager?",
        chunks,
        min_overlap=1,
        ollama=_MustNotCall(),
    )
    assert "15 minutes" in reply
    assert cites[0]["filename"] == "handbook.txt"


def test_ollama_rag_not_found_matches_extractive_pipeline() -> None:
    chunks = [
        RetrievedChunk(
            score=0.99,
            chunk_id="c1",
            document_id="d1",
            filename="x.txt",
            chunk_index=0,
            page_number=None,
            text="completely unrelated content about zebras and astronomy",
        )
    ]

    reply, cites = ollama_rag_answer(
        "what is the quarterly revenue target",
        chunks,
        min_overlap=4,
        ollama=_FakeOllamaOK(),
    )
    assert reply == NOT_FOUND
    assert cites == []


def test_drop_not_found_when_cited_removes_contradictory_refusal() -> None:
    mixed = f"The supply range is 1.8V to 3.6V [1]. {NOT_FOUND}"
    out = _drop_not_found_when_cited(mixed)
    assert "1.8" in out
    assert NOT_FOUND.lower() not in out.lower()
