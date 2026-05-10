from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    sha256: str
    source_type: str
    status: str
    page_count: int | None
    chunk_count: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DocumentDetailOut(DocumentOut):
    preview_text: str | None = Field(
        default=None,
        description="Short preview from first chunk for list UIs",
    )
