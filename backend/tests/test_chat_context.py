from __future__ import annotations

from sqlalchemy import select

from app.db.session import get_session_local
from app.main import app
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.user import User
from app.services.chat_context import rag_query_for_session
from fastapi.testclient import TestClient


def _admin_user(db) -> User:
    u = db.scalar(select(User).where(User.email == "admin@example.com"))
    assert u is not None
    return u


def test_rag_query_single_turn() -> None:
    with TestClient(app):
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            u = _admin_user(db)
            s = ChatSession(user_id=u.id, title="t")
            db.add(s)
            db.commit()
            db.refresh(s)
            db.add(ChatMessage(session_id=s.id, role="user", content="  stm32 adc  "))
            db.commit()
            assert rag_query_for_session(db, s.id, "stm32 adc") == "stm32 adc"
        finally:
            db.close()


def test_rag_query_merges_last_user_turns() -> None:
    with TestClient(app):
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            u = _admin_user(db)
            s = ChatSession(user_id=u.id, title="t")
            db.add(s)
            db.commit()
            db.refresh(s)
            for text in ("stm32f405 datasheet timers", "how many?", "the pdf you said"):
                db.add(ChatMessage(session_id=s.id, role="user", content=text))
                db.add(ChatMessage(session_id=s.id, role="assistant", content="ok"))
            db.commit()
            q = rag_query_for_session(db, s.id, "the pdf you said")
            assert "stm32f405" in q.lower()
            assert "how many" in q.lower()
            assert "the pdf you said" in q.lower()
        finally:
            db.close()
