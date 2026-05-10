from datetime import UTC, datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.models.user import User


def _fake_user() -> User:
    return User(
        id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        email="test@test.com",
        password_hash="*",
        role="owner",
        created_at=datetime.now(tz=UTC),
        last_login_at=None,
    )


def test_system_status_shape() -> None:
    fake = {
        "app": "PrivateAI Box",
        "providers": {"llm": "mock_llm", "embedding": "mock_embedding"},
        "dependencies": {
            "postgres": {"ok": True, "detail": "connected"},
            "qdrant": {"ok": True, "detail": "reachable"},
        },
        "healthy": True,
    }
    app.dependency_overrides[get_current_user] = _fake_user
    try:
        with patch("app.api.system.build_system_status", return_value=fake):
            with TestClient(app) as client:
                r = client.get("/api/system/status")
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    body = r.json()
    assert body["healthy"] is True
    assert body["dependencies"]["postgres"]["ok"] is True
