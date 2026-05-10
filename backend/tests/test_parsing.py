from pathlib import Path

from app.services.parsing import extract_pages, is_allowed_upload, normalize_extension


def test_normalize_extension() -> None:
    assert normalize_extension("FILE.PDF") == ".pdf"


def test_is_allowed_upload() -> None:
    assert is_allowed_upload("x.pdf") is True
    assert is_allowed_upload("x.exe") is False


def test_extract_txt_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("hello\nworld", encoding="utf-8")
    pages, pc = extract_pages(p, ".txt")
    assert pc is None
    assert len(pages) == 1
    assert "hello" in pages[0][1]
