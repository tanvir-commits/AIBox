from __future__ import annotations

import os
import tempfile
from unittest.mock import patch

import pytest

from app.core.config import get_settings
from app.db.session import reset_engine

# Unit tests use SQLite in-memory unless integration stack tests run in Docker.
if os.getenv("STACK_TEST") != "1":
    os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    os.environ.setdefault("QDRANT_URL", "http://127.0.0.1:6333")
    os.environ.setdefault(
        "JWT_SECRET",
        "unit-test-secret-key-at-least-32-bytes-long",
    )
    os.environ.setdefault("BOOTSTRAP_ADMIN_PASSWORD", "test-admin-password")
    os.environ.setdefault("BOOTSTRAP_ADMIN_EMAIL", "admin@example.com")
    os.environ.setdefault("UPLOAD_ROOT", tempfile.mkdtemp(prefix="pa-upload-"))


@pytest.fixture(autouse=True)
def _reset_settings_and_engine() -> None:
    get_settings.cache_clear()
    reset_engine()
    yield
    reset_engine()
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _skip_qdrant_collection_bootstrap(request: pytest.FixtureRequest) -> None:
    if request.node.get_closest_marker("integration") is not None:
        yield
        return
    with patch("app.main.ensure_collection"):
        yield
