from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_writer
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.schemas.documents import DocumentDetailOut, DocumentOut
from app.services.ingestion import delete_document_cascade, ingest_document
from app.services.parsing import is_allowed_upload, normalize_extension
from app.services.storage import safe_filename

router = APIRouter(prefix="/api/documents", tags=["documents"])


async def _save_upload_to_disk(
    upload: UploadFile,
    dest: Path,
    *,
    max_bytes: int,
) -> tuple[str, int]:
    hasher = hashlib.sha256()
    size = 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as fh:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                fh.flush()
                dest.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File too large",
                )
            hasher.update(chunk)
            fh.write(chunk)
    return hasher.hexdigest(), size


@router.get("", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[Document]:
    _ = _user
    return list(
        db.scalars(select(Document).order_by(Document.created_at.desc())).all(),
    )


@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> DocumentDetailOut:
    _ = _user
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    preview = db.scalar(
        select(DocumentChunk.text)
        .where(DocumentChunk.document_id == doc.id)
        .order_by(DocumentChunk.chunk_index.asc())
        .limit(1),
    )
    base = DocumentOut.model_validate(doc)
    snippet = (preview or "")[:400] or None
    return DocumentDetailOut(**base.model_dump(), preview_text=snippet)


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    user: User = Depends(require_writer),
) -> Document:
    if not file.filename:
        raise HTTPException(status_code=422, detail="Missing filename")
    if not is_allowed_upload(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported type. Allowed: pdf, docx, txt, md, csv.",
        )

    doc_id = str(uuid.uuid4())
    name = safe_filename(file.filename)
    relative = f"{doc_id}/{name}"
    dest = Path(settings.upload_root) / relative

    sha256, size = await _save_upload_to_disk(
        file,
        dest,
        max_bytes=settings.max_upload_bytes,
    )

    existing = db.scalar(select(Document).where(Document.sha256 == sha256))
    if existing is not None:
        dest.unlink(missing_ok=True)
        try:
            dest.parent.rmdir()
        except OSError:
            pass
        raise HTTPException(
            status_code=409,
            detail="This file was already uploaded",
        )

    ext = normalize_extension(file.filename).lstrip(".")
    doc = Document(
        id=doc_id,
        user_id=user.id,
        filename=file.filename,
        file_type=ext,
        file_size=size,
        sha256=sha256,
        source_type="upload",
        source_path=relative,
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    ingest_document(db, settings, doc.id)
    db.refresh(doc)
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    _user: User = Depends(require_writer),
) -> None:
    _ = _user
    ok = delete_document_cascade(db, settings, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found")


@router.post("/{document_id}/reindex", response_model=DocumentOut)
def reindex_document(
    document_id: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    _user: User = Depends(require_writer),
) -> Document:
    _ = _user
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    ingest_document(db, settings, doc.id)
    db.refresh(doc)
    return doc
