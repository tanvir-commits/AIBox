"""Grounded synthesis via a local Ollama model over retrieved chunks."""

from __future__ import annotations

import logging
import re
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
- If the user asks “how many” and the sources list concrete instances (e.g. TIM1, TIM2, … or ADC1, ADC2),
  give the count from that list (or say the sources only partially enumerate them) instead of refusing.
- If the sources do not contain enough information for a grounded answer, reply with exactly:
  I could not find that in the indexed company documents.
- Never use that “could not find” phrase in the same reply where you also give facts with [n] citations —
  pick one: either answer from sources or refuse entirely.
"""


class OllamaChatClient(Protocol):
    def chat(self, *, system: str, user: str) -> str: ...


def _drop_not_found_when_cited(reply: str) -> str:
    """LLMs sometimes echo NOT_FOUND after a good cited answer; strip that contradiction."""
    if NOT_FOUND.lower() not in reply.lower():
        return reply
    if not re.search(r"\[\d+\]", reply):
        return reply
    kept: list[str] = []
    for sent in re.split(r"(?<=[.!?])\s+", reply.strip()):
        s = sent.strip()
        if not s:
            continue
        if NOT_FOUND.lower() in s.lower() and len(s) <= 220:
            continue
        kept.append(sent.strip())
    out = " ".join(kept).strip()
    return out if out else reply


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
    reply = _drop_not_found_when_cited(reply)
    return reply, citations
