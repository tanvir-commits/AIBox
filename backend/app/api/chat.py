from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.user import User
from app.schemas.chat import (
    ChatMessageOut,
    ChatRequest,
    ChatSessionDetailOut,
    ChatSessionListOut,
    ChatTurnResponse,
    Citation,
)
from app.providers.ollama_llm import OllamaLLMProvider
from app.services.rag import CHITCHAT_REPLY, is_chitchat, mock_rag_answer, retrieve_chunks
from app.services.rag_ollama import ollama_rag_answer

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/sessions", response_model=list[ChatSessionListOut])
def list_sessions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ChatSession]:
    return list(
        db.scalars(
            select(ChatSession)
            .where(ChatSession.user_id == user.id)
            .order_by(ChatSession.updated_at.desc()),
        ).all(),
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailOut)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatSessionDetailOut:
    session = db.scalars(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
        .where(ChatSession.user_id == user.id),
    ).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = sorted(session.messages, key=lambda m: m.created_at)
    return ChatSessionDetailOut(
        id=session.id,
        title=session.title,
        updated_at=session.updated_at,
        messages=[ChatMessageOut.model_validate(m) for m in msgs],
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    session = db.get(ChatSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()


@router.post("", response_model=ChatTurnResponse)
def chat_turn(
    body: ChatRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    user: User = Depends(get_current_user),
) -> ChatTurnResponse:
    if body.session_id:
        session = db.get(ChatSession, body.session_id)
        if session is None or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        title = body.message.strip().replace("\n", " ")[:80] or "Chat"
        session = ChatSession(user_id=user.id, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)

    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=body.message,
        citations=None,
    )
    db.add(user_msg)
    db.flush()

    if is_chitchat(body.message):
        reply, cites_raw = CHITCHAT_REPLY, []
    else:
        chunks = retrieve_chunks(db, settings, body.message)
        provider = settings.default_llm_provider.strip().lower()
        if provider == "ollama":
            reply, cites_raw = ollama_rag_answer(
                body.message,
                chunks,
                min_overlap=settings.rag_min_token_overlap,
                ollama=OllamaLLMProvider(settings),
            )
        else:
            reply, cites_raw = mock_rag_answer(
                body.message,
                chunks,
                min_overlap=settings.rag_min_token_overlap,
            )
    cites = [Citation.model_validate(c) for c in cites_raw]

    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=reply,
        citations=[c.model_dump() for c in cites],
    )
    db.add(assistant_msg)
    session.updated_at = datetime.now(tz=UTC)
    db.commit()

    return ChatTurnResponse(
        session_id=session.id,
        reply=reply,
        citations=cites,
    )
