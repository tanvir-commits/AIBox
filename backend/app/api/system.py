from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.core.config import Settings, get_settings
from app.models.user import User
from app.services.system_status import build_system_status

router = APIRouter(tags=["system"])


@router.get("/api/system/status")
def system_status(
    _user: Annotated[User, Depends(get_current_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict:
    _ = _user
    return build_system_status(settings)
