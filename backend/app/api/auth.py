from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserPublic
from app.services.jwt_tokens import create_access_token
from app.services.passwords import verify_password

router = APIRouter(tags=["auth"])


@router.post("/api/auth/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    email = body.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    user.last_login_at = datetime.now(tz=UTC)
    db.add(user)
    db.commit()
    token = create_access_token(
        subject=user.id,
        role=user.role,
        settings=settings,
    )
    return TokenResponse(access_token=token)


@router.post("/api/auth/logout")
def logout() -> dict[str, bool]:
    return {"ok": True}


@router.get("/api/auth/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)) -> User:
    return user
