from __future__ import annotations

import re
from dataclasses import dataclass

# Sentence boundary with following whitespace (handles most PDF plaintext).
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])(?:\s+|$)")


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    page_number: int | None
    text: str


def _trim_leading_sentence_fragment(piece: str) -> str:
    """If chunk starts mid-clause on a lowercase letter, try to align to sentence start."""
    s = piece.strip()
    if not s:
        return s
    if not s[0].isalpha() or not s[0].islower():
        return s
    pref = min(560, len(s))
    boundary_matches = list(_SENTENCE_BREAK.finditer(s[:pref]))
    for m in reversed(boundary_matches):
        tail = s[m.end() :].lstrip()
        if not tail:
            continue
        if tail[0].isupper() or tail[0].isdigit():
            return tail if len(tail) >= 40 else ("… " + s)
    return "… " + s


def _split_with_overlap(text: str, max_chars: int, overlap: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [_trim_leading_sentence_fragment(text)]

    raw: list[str] = []
    start = 0
    iterations = 0
    min_piece = max(80, max_chars // 12)

    while start < len(text) and iterations < 2500:
        iterations += 1
        soft_end = min(len(text), start + max_chars)
        end = soft_end

        if soft_end < len(text):
            segment = text[start:soft_end]
            last_cut = None
            for m in _SENTENCE_BREAK.finditer(segment):
                if m.end() >= min_piece:
                    last_cut = m.end()
            if last_cut:
                end = start + last_cut

        slice_ = text[start:end].strip()
        if slice_:
            raw.append(slice_)

        if end >= len(text):
            break

        next_start = end - overlap
        next_start = max(start + min_piece // 4, next_start)
        if next_start >= len(text):
            break
        if next_start <= start:
            next_start = end

        start = next_start

    trimmed = [_trim_leading_sentence_fragment(p) for p in raw if len(p.strip()) >= 28]
    return trimmed


def pages_to_chunks(
    pages: list[tuple[int | None, str]],
    *,
    max_chars: int = 1200,
    overlap: int = 200,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    idx = 0
    for page_number, page_text in pages:
        for piece in _split_with_overlap(page_text, max_chars, overlap):
            if not piece.strip():
                continue
            chunks.append(TextChunk(chunk_index=idx, page_number=page_number, text=piece))
            idx += 1
    return chunks


def approx_token_count(text: str) -> int:
    return max(1, len(text) // 4)
