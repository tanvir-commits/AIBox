"""Grounded synthesis via a local Ollama model over retrieved chunks."""

from __future__ import annotations

import logging
from typing import Protocol

from app.services.rag import (
    NOT_FOUND,
    RAGHitOutcome,
    RAGSpecialOutcome,
    RetrievedChunk,
    build_citations_for_answer,
    evaluate_rag_for_answer,
    extractive_rag_answer_from_hit,
    sanitize_extracted_text,
)

logger = logging.getLogger(__name__)

_CONTEXT_CHARS = 2600

_SYSTEM = """You answer questions using ONLY the numbered sources provided below.
Rules:
- Prefer a direct answer in plain language (2–6 short paragraphs max unless the user asks for detail).
- When you state a specific fact from a source, add an inline citation like [1] or [2] matching that source index.
- Do not invent policies, figures, dates, pin names, or product behavior that are not explicit in the sources.
- Do not cite or mention filenames inside the prose — only use [n] citations.
- Do not ask the user which document or PDF they mean, and do not ask them to paste more context — use the
  thread lines and sources you already have. If the latest message is vague, infer intent from earlier lines.
- If the sources do not contain enough information for a grounded answer, reply with exactly:
  I could not find that in the indexed company documents.
"""


class OllamaChatClient(Protocol):
    def chat(self, *, system: str, user: str) -> str: ...


def _chunk_by_citation_lookup(hit: RAGHitOutcome, citations: list[dict]) -> dict[str, RetrievedChunk]:
    by_id = {hit.primary.chunk_id: hit.primary}
    for c in hit.ranked:
        by_id[c.chunk_id] = c
    return {cid: by_id[cid] for cid in (c["chunk_id"] for c in citations) if cid in by_id}


def _build_user_prompt(
    question: str,
    citations: list[dict],
    chunks: dict[str, RetrievedChunk],
    *,
    latest_user_message: str | None,
) -> str | None:
    blocks: list[str] = []
    for i, cd in enumerate(citations, start=1):
        cid = cd["chunk_id"]
        ch = chunks.get(cid)
        if ch is None:
            continue
        txt = sanitize_extracted_text(ch.text)
        trimmed = txt[:_CONTEXT_CHARS] if len(txt) > _CONTEXT_CHARS else txt
        pg = str(ch.page_number) if ch.page_number is not None else "?"
        blocks.append(f"[{i}] {ch.filename} (page {pg})\n{trimmed}")
    if not blocks:
        return None
    body = "\n\n---\n\n".join(blocks)
    if latest_user_message and latest_user_message.strip() != question.strip():
        qblock = (
            f"Latest user message (answer this):\n{latest_user_message.strip()}\n\n"
            f"Earlier user lines in this chat (context for retrieval):\n{question.strip()}"
        )
    else:
        qblock = question.strip()
    return f"Question:\n{qblock}\n\nSources:\n{body}"


def ollama_rag_answer(
    question: str,
    chunks: list[RetrievedChunk],
    *,
    min_overlap: int,
    ollama: OllamaChatClient,
    latest_user_message: str | None = None,
) -> tuple[str, list[dict]]:
    out = evaluate_rag_for_answer(question, chunks, min_overlap=min_overlap)
    if out is None:
        return NOT_FOUND, []
    if isinstance(out, RAGSpecialOutcome):
        return out.reply, out.citations

    hit: RAGHitOutcome = out
    citations = build_citations_for_answer(question, hit.primary, hit.ranked)
    if not citations:
        return extractive_rag_answer_from_hit(question, hit)

    by_c = _chunk_by_citation_lookup(hit, citations)
    user_prompt = _build_user_prompt(
        question,
        citations,
        by_c,
        latest_user_message=latest_user_message,
    )
    if user_prompt is None:
        return extractive_rag_answer_from_hit(question, hit)

    try:
        reply = ollama.chat(system=_SYSTEM, user=user_prompt).strip()
    except Exception as exc:
        logger.warning("Ollama chat failed (%s); using extractive RAG fallback", exc)
        return extractive_rag_answer_from_hit(question, hit)

    if not reply:
        return extractive_rag_answer_from_hit(question, hit)
    return reply, citations
