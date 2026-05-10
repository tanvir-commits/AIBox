from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=1, max_length=8000)


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    filename: str
    page_number: int | None = None
    excerpt: str


class ChatTurnResponse(BaseModel):
    session_id: str
    reply: str
    citations: list[Citation]


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    citations: list[dict[str, Any]] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionListOut(BaseModel):
    id: str
    title: str
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChatSessionDetailOut(BaseModel):
    id: str
    title: str
    updated_at: datetime | None = None
    messages: list[ChatMessageOut]

    model_config = {"from_attributes": True}
