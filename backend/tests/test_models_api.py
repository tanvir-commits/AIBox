from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


def _token(client: TestClient) -> str:
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "test-admin-password"},
    )
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


def test_ollama_models_when_provider_is_mock() -> None:
    with TestClient(app) as client:
        token = _token(client)
        r = client.get("/api/models/ollama", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["reachable"] is False
    assert body["models"] == []
    assert "not ollama" in (body.get("detail") or "").lower()


def test_ollama_models_lists_tags_when_ollama_enabled() -> None:
    fake_tags = {
        "models": [
            {"name": "llama3.2:latest", "size": 123, "modified_at": "2025-01-01T00:00:00Z"},
        ]
    }

    def fake_get_settings() -> Settings:
        return Settings(
            default_llm_provider="ollama",
            ollama_model="llama3.2:latest",
            ollama_base_url="http://127.0.0.1:11434",
        )

    with patch("app.api.models.fetch_ollama_tags", return_value=fake_tags):
        app.dependency_overrides[get_settings] = fake_get_settings
        try:
            with TestClient(app) as client:
                token = _token(client)
                r = client.get(
                    "/api/models/ollama",
                    headers={"Authorization": f"Bearer {token}"},
                )
        finally:
            app.dependency_overrides.clear()

    assert r.status_code == 200
    body = r.json()
    assert body["reachable"] is True
    assert len(body["models"]) == 1
    assert body["models"][0]["name"] == "llama3.2:latest"
