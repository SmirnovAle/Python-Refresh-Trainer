from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_user_id
from app.schemas import ProgressSummary
from app.services.progress_service import get_default_user, get_progress_summary

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/summary", response_model=ProgressSummary)
def progress_summary(
    user_id: int = Depends(require_user_id),
    db: Session = Depends(get_db),
) -> ProgressSummary:
    user = get_default_user(db, user_id)
    summary = get_progress_summary(db, user)
    return ProgressSummary(**summary)
