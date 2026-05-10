from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.user import User
from app.services.passwords import hash_password

logger = logging.getLogger(__name__)


def ensure_bootstrap_admin(session: Session, settings: Settings) -> None:
    if not settings.bootstrap_admin_password:
        return
    email = settings.bootstrap_admin_email.strip().lower()
    existing = session.scalar(select(User).where(User.email == email))
    if existing:
        return
    user = User(
        email=email,
        password_hash=hash_password(settings.bootstrap_admin_password),
        role="owner",
    )
    session.add(user)
    session.commit()
    logger.info("bootstrap admin created for %s", email)
