from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import Settings


def create_access_token(
    *,
    subject: str,
    role: str,
    settings: Settings,
) -> str:
    now = datetime.now(tz=UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str, settings: Settings) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
