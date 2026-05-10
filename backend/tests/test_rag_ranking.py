from app.services.rag import (
    RetrievedChunk,
    filename_domain_boost,
    mock_rag_answer,
    prose_quality_score,
    rerank_chunks_for_qa,
    sanitize_extracted_text,
)


def test_prose_scores_table_lower_than_prose() -> None:
    table = "1 , 0s 0s 1 , 0s s 1 , 1s 1s 1 , 1s s 1 , 2s s 1"
    prose = (
        "The AES algorithm operates on 128-bit blocks using keys of 128, 192, or 256 bits "
        "according to this standard."
    )
    assert prose_quality_score(sanitize_extracted_text(table)) < prose_quality_score(
        sanitize_extracted_text(prose)
    )


def test_filename_boost_matches_nist_for_aes_question() -> None:
    q = "What is the AES block size in bits?"
    assert filename_domain_boost(q, "nist-crypto.pdf") > filename_domain_boost(q, "dm00037051.pdf")


def test_rerank_prefers_nist_chunk_for_aes_block_question() -> None:
    stm32 = RetrievedChunk(
        0.95,
        "s1",
        "dS",
        "dm00037051.pdf",
        0,
        21,
        "STM32F405xx Arm Cortex-M4 processor with FPU embedded flash and SRAM.",
    )
    nist = RetrievedChunk(
        0.55,
        "s2",
        "dN",
        "nist-crypto.pdf",
        0,
        10,
        "The AES algorithm operates on 128-bit blocks using keys of 128, 192, or 256 bits.",
    )
    ranked = rerank_chunks_for_qa("What is the AES block size in bits?", [stm32, nist])
    assert ranked[0].filename == "nist-crypto.pdf"


def test_stm32_aes_question_prefers_datasheet_over_nist_notice() -> None:
    nist = RetrievedChunk(
        0.95,
        "n1",
        "dN",
        "nist-crypto.pdf",
        0,
        1,
        "Warning notice: This publication has been withdrawn and archived for historical purposes. AES",
    )
    ds = RetrievedChunk(
        0.35,
        "s1",
        "dS",
        "dm00037051.pdf",
        0,
        88,
        "The STM32F405xx and STM32F407xx include a CRYP crypto processor and AES hardware.",
    )
    ranked = rerank_chunks_for_qa("does stm32 have AES", [nist, ds])
    assert ranked[0].filename == "dm00037051.pdf"


def test_mock_rag_answer_aes_prefers_nist_document() -> None:
    stm32 = RetrievedChunk(
        0.95,
        "s1",
        "dS",
        "dm00037051.pdf",
        0,
        21,
        "STM32F405xx Arm Cortex-M4 processor with FPU embedded flash and SRAM.",
    )
    nist = RetrievedChunk(
        0.55,
        "s2",
        "dN",
        "nist-crypto.pdf",
        0,
        10,
        "The AES algorithm operates on 128-bit blocks using keys of 128, 192, or 256 bits.",
    )
    reply, cites = mock_rag_answer(
        "What is the AES block size in bits?",
        [stm32, nist],
        min_overlap=1,
    )
    assert "128" in reply
    assert cites[0]["filename"] == "nist-crypto.pdf"
