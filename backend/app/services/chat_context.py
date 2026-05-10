"""Merge recent user turns so short follow-ups still retrieve well."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage

_MAX_RAG_QUERY_CHARS = 4500
_MAX_USER_TURNS = 4


def ordered_user_contents(db: Session, session_id: str) -> list[str]:
    rows = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc()),
    ).all()
    return [m.content.strip() for m in rows if m.role == "user" and m.content.strip()]


def rag_query_for_session(db: Session, session_id: str, latest_user_message: str) -> str:
    """
    Single string for vector + keyword retrieval and RAG overlap gates.
    After the first user turn, concatenate the last few user messages so
    pronouns / “that PDF” / “how many?” still carry product keywords from earlier turns.
    """
    parts = ordered_user_contents(db, session_id)
    if len(parts) <= 1:
        return latest_user_message.strip()
    tail = parts[-_MAX_USER_TURNS :]
    merged = "\n".join(tail).strip()
    if len(merged) > _MAX_RAG_QUERY_CHARS:
        merged = merged[-_MAX_RAG_QUERY_CHARS:]
    return merged
