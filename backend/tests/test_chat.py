from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.rag import CHITCHAT_REPLY, RetrievedChunk


def _headers(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "test-admin-password"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_chat_chitchat_skips_retrieval() -> None:
    def _should_not_run(*_a, **_k):
        raise AssertionError("retrieve_chunks must not run for chitchat")

    with patch("app.api.chat.retrieve_chunks", side_effect=_should_not_run):
        with TestClient(app) as client:
            h = _headers(client)
            r = client.post("/api/chat", headers=h, json={"message": "Hello!"})
    assert r.status_code == 200, r.text
    assert r.json()["reply"] == CHITCHAT_REPLY
    assert r.json()["citations"] == []


def test_chat_turn_with_mocked_retrieval() -> None:
    canned = [
        RetrievedChunk(
            score=0.88,
            chunk_id="chunk-1",
            document_id="doc-1",
            filename="note.txt",
            chunk_index=0,
            page_number=None,
            text="Revenue target for Q3 is forty two million dollars.",
        )
    ]

    with patch("app.api.chat.retrieve_chunks", return_value=canned):
        with TestClient(app) as client:
            h = _headers(client)
            r = client.post(
                "/api/chat",
                headers=h,
                json={"message": "What is the Q3 revenue target?"},
            )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "session_id" in body
    assert "forty two million" in body["reply"].lower()
    assert len(body["citations"]) >= 1


def test_chat_second_turn_merges_prior_user_text_for_retrieval() -> None:
    captured: list[str] = []

    def capture_retrieve(db, settings, q):  # noqa: ANN001
        captured.append(q)
        return []

    with patch("app.api.chat.retrieve_chunks", side_effect=capture_retrieve):
        with TestClient(app) as client:
            h = _headers(client)
            first = client.post(
                "/api/chat",
                headers=h,
                json={"message": "stm32f405 datasheet timers"},
            )
            assert first.status_code == 200
            sid = first.json()["session_id"]
            assert "stm32f405" in captured[-1].lower()

            second = client.post(
                "/api/chat",
                headers=h,
                json={"session_id": sid, "message": "how many timers?"},
            )
            assert second.status_code == 200
            merged = captured[-1].lower()
            assert "stm32f405" in merged
            assert "how many" in merged


def test_chat_session_roundtrip() -> None:
    with patch("app.api.chat.retrieve_chunks", return_value=[]):
        with TestClient(app) as client:
            h = _headers(client)
            first = client.post(
                "/api/chat",
                headers=h,
                json={"message": "hello there"},
            )
            sid = first.json()["session_id"]
            second = client.post(
                "/api/chat",
                headers=h,
                json={"session_id": sid, "message": "follow up"},
            )
            assert second.json()["session_id"] == sid

            listed = client.get("/api/chat/sessions", headers=h)
            assert listed.status_code == 200
            assert any(s["id"] == sid for s in listed.json())

            detail = client.get(f"/api/chat/sessions/{sid}", headers=h)
            assert detail.status_code == 200
            assert len(detail.json()["messages"]) >= 4

            deleted = client.delete(f"/api/chat/sessions/{sid}", headers=h)
            assert deleted.status_code == 204
