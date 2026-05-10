from __future__ import annotations

import logging
import uuid
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.providers.mock_embedding import MockEmbeddingProvider
from app.services.chunking import approx_token_count, pages_to_chunks
from app.services.parsing import extract_pages, normalize_extension
from app.services.qdrant_chunks import delete_document_vectors, upsert_chunks

logger = logging.getLogger(__name__)

_PAYLOAD_TEXT_MAX = 8000


def ingest_document(db: Session, settings: Settings, document_id: str) -> None:
    doc = db.get(Document, document_id)
    if doc is None:
        return

    path = Path(settings.upload_root) / doc.source_path
    ext = normalize_extension(doc.filename)
    if not path.exists():
        raise FileNotFoundError(f"Stored file missing: {path}")

    try:
        try:
            delete_document_vectors(settings, doc.id)
        except Exception:  # noqa: BLE001
            pass
        db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc.id))
        db.commit()

        doc.status = "parsing"
        doc.error_message = None
        db.commit()

        pages, page_count = extract_pages(path, ext)
        doc.page_count = page_count
        doc.status = "parsed"
        db.commit()

        text_chunks = pages_to_chunks(pages)
        if not text_chunks:
            raise ValueError("No extractable text from document")

        doc.status = "embedding"
        db.commit()

        embedder = MockEmbeddingProvider()
        points: list[tuple[str, list[float], dict]] = []
        rows: list[DocumentChunk] = []

        for tc in text_chunks:
            point_id = str(uuid.uuid4())
            vector = embedder.embed(tc.text)
            payload = {
                "document_id": doc.id,
                "chunk_id": point_id,
                "chunk_index": tc.chunk_index,
                "page_number": tc.page_number,
                "text": tc.text[:_PAYLOAD_TEXT_MAX],
            }
            points.append((point_id, vector, payload))
            rows.append(
                DocumentChunk(
                    id=point_id,
                    document_id=doc.id,
                    chunk_index=tc.chunk_index,
                    page_number=tc.page_number,
                    text=tc.text,
                    token_count=approx_token_count(tc.text),
                    qdrant_point_id=point_id,
                )
            )

        upsert_chunks(settings, document_id=doc.id, points=points)
        db.add_all(rows)
        doc.chunk_count = len(rows)
        doc.status = "indexed"
        db.commit()
    except Exception as exc:  # noqa: BLE001
        logger.exception("ingestion failed for %s", document_id)
        doc.status = "failed"
        doc.error_message = str(exc)[:4000]
        db.commit()


def delete_document_cascade(
    db: Session,
    settings: Settings,
    document_id: str,
) -> bool:
    doc = db.get(Document, document_id)
    if doc is None:
        return False
    try:
        delete_document_vectors(settings, document_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("qdrant delete failed (continuing): %s", exc)
    folder = Path(settings.upload_root) / document_id
    if folder.exists():
        for child in folder.iterdir():
            child.unlink(missing_ok=True)
        try:
            folder.rmdir()
        except OSError:
            logger.warning("could not remove upload folder %s", folder)
    db.delete(doc)
    db.commit()
    return True
