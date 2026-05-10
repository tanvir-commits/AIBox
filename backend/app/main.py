from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, chat, documents, health, system
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_engine, get_session_local
import app.models  # noqa: F401 — register ORM metadata on Base
from app.providers.embedding_provider import get_embedding_provider
from app.services.bootstrap import ensure_bootstrap_admin
from app.services.qdrant_chunks import ensure_collection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    embedder = get_embedding_provider(settings)
    logger.info(
        "embedding provider=%s model=%s dim=%s — if you changed embedding backends, "
        "clear Qdrant data and re-ingest documents for consistent retrieval",
        embedder.name,
        getattr(embedder, "model_name", "n/a"),
        embedder.dimensions,
    )
    ensure_collection(settings, embedder.dimensions)
    try:
        embedder.embed("__embedding_warmup__")
    except Exception:
        logger.exception(
            "embedding warmup failed — first document ingest may also fail until the model loads",
        )
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        ensure_bootstrap_admin(db, settings)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Local AI appliance API — Phases 0–4 (bootstrap, auth, documents, mock RAG chat).",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        _ = request
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Request validation failed.",
                "details": exc.errors(),
            },
        )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(chat.router)
    app.include_router(system.router)
    return app


app = create_app()
