"""Live dependency checks; run in Docker with STACK_TEST=1 (see docker-compose.test.yml)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

from app.main import app  # noqa: E402


@pytest.mark.skipif(os.getenv("STACK_TEST") != "1", reason="STACK_TEST=1 required")
def test_system_status_against_real_stack() -> None:
    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login",
            json={
                "email": "admin@example.com",
                "password": "changeme",
            },
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        r = client.get(
            "/api/system/status",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["healthy"] is True
    assert body["dependencies"]["postgres"]["ok"] is True
    assert body["dependencies"]["qdrant"]["ok"] is True


@pytest.mark.skipif(os.getenv("STACK_TEST") != "1", reason="STACK_TEST=1 required")
def test_upload_txt_end_to_end() -> None:
    from io import BytesIO

    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "changeme"},
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        files = {
            "file": (
                "integration.txt",
                BytesIO(b"Integration upload body.\nSecond line."),
                "text/plain",
            ),
        }
        up = client.post("/api/documents/upload", headers=headers, files=files)
        assert up.status_code == 201, up.text
        doc_id = up.json()["id"]
        assert up.json()["status"] == "indexed"

        listed = client.get("/api/documents", headers=headers)
        assert listed.status_code == 200
        ids = {d["id"] for d in listed.json()}
        assert doc_id in ids

        delete = client.delete(f"/api/documents/{doc_id}", headers=headers)
        assert delete.status_code == 204


@pytest.mark.skipif(os.getenv("STACK_TEST") != "1", reason="STACK_TEST=1 required")
def test_chat_rag_uses_indexed_fixture() -> None:
    from pathlib import Path

    sample = Path(__file__).resolve().parent / "fixtures" / "sample.txt"
    body = sample.read_bytes()

    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "changeme"},
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        files = {"file": ("sample.txt", body, "text/plain")}
        up = client.post("/api/documents/upload", headers=headers, files=files)
        assert up.status_code == 201, up.text
        assert up.json()["status"] == "indexed"
        doc_id = up.json()["id"]

        chat = client.post(
            "/api/chat",
            headers=headers,
            json={
                "message": "How fast do staff need to notify the office manager?",
            },
        )
        assert chat.status_code == 200, chat.text
        payload = chat.json()
        assert "15 minutes" in payload["reply"]
        assert len(payload["citations"]) >= 1

        client.delete(f"/api/documents/{doc_id}", headers=headers)
