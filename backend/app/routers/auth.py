from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import AuthConfigResponse, LoginRequest, RegisterRequest, UserOut
from app.services.auth_service import (
    EmailTakenError,
    InvalidRegistrationError,
    RegistrationDisabledError,
    UserLimitError,
    create_access_token,
    normalize_email,
    register_user,
    touch_last_login,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, user_id: int) -> None:
    token = create_access_token(user_id)
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.jwt_expire_hours * 3600,
        path="/",
    )


@router.get("/config", response_model=AuthConfigResponse)
def auth_config() -> AuthConfigResponse:
    return AuthConfigResponse(registration_enabled=settings.registration_enabled)


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> User:
    try:
        user = register_user(
            db,
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
    except RegistrationDisabledError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except UserLimitError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except EmailTakenError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidRegistrationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _set_auth_cookie(response, user.id)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    email = normalize_email(payload.email)
    user = db.query(User).filter(User.email == email).first()
    if user is None or user.password_hash is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    touch_last_login(db, user)
    _set_auth_cookie(response, user.id)
    return user


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=settings.cookie_name,
        path="/",
        secure=settings.cookie_secure,
        samesite="lax",
    )
    return {"status": "ok"}
