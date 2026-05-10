from __future__ import annotations

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def _auth_headers(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "test-admin-password"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_txt_indexes_with_mocked_qdrant(tmp_path: Path) -> None:
    with patch("app.services.ingestion.upsert_chunks"), patch(
        "app.services.ingestion.delete_document_vectors",
    ):
        with TestClient(app) as client:
            headers = _auth_headers(client)
            body = b"Phase three upload content.\nSecond line."
            files = {"file": ("note.txt", BytesIO(body), "text/plain")}
            r = client.post("/api/documents/upload", headers=headers, files=files)
    assert r.status_code == 201, r.text
    doc = r.json()
    assert doc["status"] == "indexed"
    assert doc["chunk_count"] >= 1


def test_duplicate_upload_conflict() -> None:
    content = b"same-bytes-for-dup-test"
    with patch("app.services.ingestion.upsert_chunks"), patch(
        "app.services.ingestion.delete_document_vectors",
    ):
        with TestClient(app) as client:
            headers = _auth_headers(client)
            files = {"file": ("a.txt", BytesIO(content), "text/plain")}
            first = client.post("/api/documents/upload", headers=headers, files=files)
            assert first.status_code == 201
            second = client.post("/api/documents/upload", headers=headers, files=files)
            assert second.status_code == 409
