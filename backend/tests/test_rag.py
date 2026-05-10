from app.services.rag import NOT_FOUND, RetrievedChunk, format_snippet, mock_rag_answer


def test_mock_rag_not_found_when_no_chunks() -> None:
    reply, cites = mock_rag_answer("any question?", [], min_overlap=1)
    assert reply == NOT_FOUND
    assert cites == []


def test_mock_rag_fixture_emergency_answer() -> None:
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
    reply, cites = mock_rag_answer(
        "How fast do staff need to notify the office manager?",
        chunks,
        min_overlap=1,
    )
    assert "15 minutes" in reply
    assert len(cites) == 1
    assert cites[0]["filename"] == "handbook.txt"


def test_mock_rag_not_found_on_zero_overlap_when_enough_question_tokens() -> None:
    chunks = [
        RetrievedChunk(
            score=0.5,
            chunk_id="c1",
            document_id="d1",
            filename="a.txt",
            chunk_index=0,
            page_number=None,
            text="completely unrelated content about zebras and astronomy",
        )
    ]
    reply, cites = mock_rag_answer(
        "what is the quarterly revenue target",
        chunks,
        min_overlap=1,
    )
    assert reply == NOT_FOUND
    assert cites == []


def test_mock_rag_not_found_greeting_with_irrelevant_chunk() -> None:
    chunks = [
        RetrievedChunk(
            score=0.99,
            chunk_id="c1",
            document_id="d1",
            filename="datasheet.pdf",
            chunk_index=0,
            page_number=51,
            text="STM32F405 pin PA0 alternate function table | LQFP64 | ...",
        )
    ]
    reply, cites = mock_rag_answer("hello", chunks, min_overlap=1)
    assert reply == NOT_FOUND
    assert cites == []


def test_aes_snippet_prefers_definition_over_preamble() -> None:
    blob = (
        "Federal Information Processing Standards Publication 197 November 26, 2001. "
        "The AES algorithm operates on 128-bit blocks using keys of 128, 192, or 256 bits."
    )
    out = format_snippet(blob, max_chars=400, question="What is the AES block size in bits?")
    assert "128" in out
    assert "Federal Information Processing" not in out


def test_format_snippet_repairs_leading_pdf_glitch() -> None:
    raw = "uality while being more parallelizable and requiring less time to train."
    out = format_snippet(raw, max_chars=300)
    assert not out.lower().startswith("uality")
    assert "while being" in out.lower() or "parallelizable" in out.lower()


def test_format_snippet_strips_model_tokens_and_dup_sentences() -> None:
    raw = (
        "Input-Input Layer5 The Law will never be perfect , but its application should be "
        "just - this is what we are missing , in my opinion . <EOS> <pad> The Law will never "
        "be perfect , but its application should be just - this is what we are missing , "
        "in my opinion ."
    )
    out = format_snippet(raw, max_chars=800)
    assert "<EOS>" not in out and "<pad>" not in out.lower()
    assert "Input-Input" not in out
    # One copy of the sentence, not two
    assert out.lower().count("the law will never be perfect") == 1


def test_mock_rag_single_keyword_matches_chunk() -> None:
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
    reply, cites = mock_rag_answer("stm32", chunks, min_overlap=1)
    assert "STM32" in reply or "stm32" in reply.lower()
    assert cites and cites[0]["filename"] == "ref.pdf"
