from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies.auth import require_user_id
from app.models import Exercise
from app.schemas import AiExplainRequest, AiExplainResponse
from app.services.ai_service import AiNotConfiguredError, AiServiceError, explain_exercise_failure
from app.services.progress_service import get_default_user, is_level_available

router = APIRouter(prefix="/ai", tags=["ai"])


def _get_exercise_or_404(db: Session, exercise_id: int) -> Exercise:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return exercise


@router.post("/explain", response_model=AiExplainResponse)
def explain_error(
    payload: AiExplainRequest,
    user_id: int = Depends(require_user_id),
    db: Session = Depends(get_db),
) -> AiExplainResponse:
    user = get_default_user(db, user_id)
    exercise = _get_exercise_or_404(db, payload.exercise_id)

    if not is_level_available(user.level, exercise.min_user_level):
        raise HTTPException(status_code=403, detail="Задание недоступно на вашем уровне")

    try:
        explanation, model_used = explain_exercise_failure(
            title=exercise.title,
            description=exercise.description,
            function_name=exercise.function_name,
            hint=exercise.hint,
            code=payload.code,
            error=payload.error,
            stderr=payload.stderr,
            failed_tests=payload.failed_tests,
        )
    except AiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AiServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AiExplainResponse(explanation=explanation, model=model_used)


@router.get("/status")
def ai_status() -> dict[str, bool | str]:
    return {
        "enabled": settings.ai_enabled,
        "configured": settings.ai_enabled and bool(settings.openai_api_key),
        "model": settings.ai_model,
        "provider": "openrouter" if "openrouter.ai" in settings.ai_base_url else "openai-compatible",
    }
