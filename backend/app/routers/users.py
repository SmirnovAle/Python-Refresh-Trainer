from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_user_id
from app.models import User
from app.schemas import UserLevelUpdate, UserOut
from app.services.progress_service import get_default_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_current_user(
    user_id: int = Depends(require_user_id),
    db: Session = Depends(get_db),
) -> User:
    try:
        return get_default_user(db, user_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/me/level", response_model=UserOut)
def update_user_level(
    payload: UserLevelUpdate,
    user_id: int = Depends(require_user_id),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.level = payload.level
    db.commit()
    db.refresh(user)
    return user
