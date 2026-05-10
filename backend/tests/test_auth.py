from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_login_bootstrap_user() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/auth/login",
            json={
                "email": "admin@example.com",
                "password": "test-admin-password",
            },
        )
    assert r.status_code == 200
    data = r.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_login_invalid_password() -> None:
    with TestClient(app) as client:
        r = client.post(
            "/api/auth/login",
            json={
                "email": "admin@example.com",
                "password": "wrong",
            },
        )
    assert r.status_code == 401


def test_me_requires_auth() -> None:
    with TestClient(app) as client:
        r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_with_token() -> None:
    with TestClient(app) as client:
        login = client.post(
            "/api/auth/login",
            json={
                "email": "admin@example.com",
                "password": "test-admin-password",
            },
        )
        token = login.json()["access_token"]
        r = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "admin@example.com"
    assert body["role"] == "owner"
