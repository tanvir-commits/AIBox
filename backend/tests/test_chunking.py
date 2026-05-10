from app.services.chunking import approx_token_count, pages_to_chunks


def test_pages_to_chunks_splits_long_page() -> None:
    long = "word " * 500
    chunks = pages_to_chunks([(1, long)], max_chars=200, overlap=20)
    assert len(chunks) >= 2
    assert all(c.page_number == 1 for c in chunks)


def test_approx_token_count() -> None:
    assert approx_token_count("abcd") == 1
