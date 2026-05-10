from __future__ import annotations

import csv
import io
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}


def normalize_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_allowed_upload(filename: str) -> bool:
    return normalize_extension(filename) in ALLOWED_EXTENSIONS


def extract_pages(path: Path, ext: str) -> tuple[list[tuple[int | None, str]], int | None]:
    """
    Returns (segments, page_count) where each segment is (page_number, text).
    page_number is 1-based for PDF pages; None for non-paginated sources.
    """
    ext = ext.lower()
    if ext == ".pdf":
        reader = PdfReader(str(path))
        pages: list[tuple[int | None, str]] = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append((i, text))
        return pages, len(reader.pages)

    if ext == ".docx":
        doc = DocxDocument(str(path))
        parts = [p.text for p in doc.paragraphs if p.text]
        body = "\n".join(parts).strip()
        return [(None, body)], None

    if ext in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        return [(None, text)], None

    if ext == ".csv":
        raw = path.read_text(encoding="utf-8", errors="replace")
        buf = io.StringIO(raw)
        reader = csv.reader(buf)
        rows = [" | ".join(row) for row in reader]
        text = "\n".join(rows).strip()
        return [(None, text)], None

    raise ValueError(f"Unsupported extension: {ext}")
