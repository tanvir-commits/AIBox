from __future__ import annotations

import logging
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from app.core.config import Settings

logger = logging.getLogger(__name__)


def qdrant_client(settings: Settings) -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url, timeout=120)


def ensure_collection(settings: Settings, vector_size: int) -> None:
    client = qdrant_client(settings)
    name = settings.qdrant_collection
    existing = {c.name for c in client.get_collections().collections}
    if name in existing:
        info = client.get_collection(collection_name=name)
        vcfg = info.config.params.vectors
        current_size: int | None = None
        if isinstance(vcfg, dict):
            for _k, vp in vcfg.items():
                if hasattr(vp, "size"):
                    current_size = int(vp.size)
                    break
        elif vcfg is not None and hasattr(vcfg, "size"):
            current_size = int(vcfg.size)
        if current_size is not None and current_size != vector_size:
            logger.warning(
                "recreating qdrant collection %s (vector size %s -> %s)",
                name,
                current_size,
                vector_size,
            )
            client.delete_collection(collection_name=name)
        elif current_size == vector_size:
            return

    logger.info("creating qdrant collection %s dim=%s", name, vector_size)
    client.create_collection(
        collection_name=name,
        vectors_config=qm.VectorParams(size=vector_size, distance=qm.Distance.COSINE),
    )


def upsert_chunks(
    settings: Settings,
    *,
    document_id: str,
    points: list[tuple[str, list[float], dict[str, Any]]],
) -> None:
    if not points:
        return
    client = qdrant_client(settings)
    batch = [
        qm.PointStruct(id=pid, vector=vec, payload=payload)
        for pid, vec, payload in points
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=batch)


def search_similar(
    settings: Settings,
    *,
    query_vector: list[float],
    limit: int,
) -> list:
    client = qdrant_client(settings)
    return client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        limit=limit,
        with_payload=True,
    )


def delete_document_vectors(settings: Settings, document_id: str) -> None:
    client = qdrant_client(settings)
    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=qm.FilterSelector(
            filter=qm.Filter(
                must=[
                    qm.FieldCondition(
                        key="document_id",
                        match=qm.MatchValue(value=document_id),
                    )
                ]
            )
        ),
    )
