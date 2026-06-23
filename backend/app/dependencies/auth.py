from fastapi import Cookie, HTTPException

from app.config import settings
from app.services.auth_service import decode_access_token


def require_user_id(trainer_token: str | None = Cookie(default=None, alias=settings.cookie_name)) -> int:
    if not settings.auth_enabled:
        return settings.default_user_id

    if not trainer_token:
        raise HTTPException(status_code=401, detail="Требуется вход")

    try:
        return decode_access_token(trainer_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Сессия истекла") from exc
