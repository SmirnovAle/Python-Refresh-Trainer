from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Exercise, Progress, ProgressStatus
from app.routers.users import resolve_user_id
from app.schemas import (
    ExerciseDetail,
    HintResponse,
    SolutionResponse,
    SubmitCodeRequest,
    SubmitCodeResponse,
)
from app.services.code_runner import CodeValidationError, run_user_code
from app.services.progress_service import get_default_user, is_level_available, upsert_progress

router = APIRouter(prefix="/exercises", tags=["exercises"])


def _get_exercise_or_404(db: Session, exercise_id: int) -> Exercise:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return exercise


@router.get("/{exercise_id}", response_model=ExerciseDetail)
def get_exercise(
    exercise_id: int,
    user_id: int = Depends(resolve_user_id),
    db: Session = Depends(get_db),
) -> ExerciseDetail:
    user = get_default_user(db, user_id)
    exercise = _get_exercise_or_404(db, exercise_id)

    if not is_level_available(user.level, exercise.min_user_level):
        raise HTTPException(status_code=403, detail="Задание недоступно на вашем уровне")

    progress = (
        db.query(Progress)
        .filter(
            Progress.user_id == user_id,
            Progress.exercise_id == exercise_id,
        )
        .first()
    )

    return ExerciseDetail(
        id=exercise.id,
        topic_id=exercise.topic_id,
        topic_slug=exercise.topic.slug,
        topic_title=exercise.topic.title,
        title=exercise.title,
        description=exercise.description,
        starter_code=exercise.starter_code,
        hint=exercise.hint,
        solution=exercise.solution,
        function_name=exercise.function_name,
        difficulty=exercise.difficulty,
        min_user_level=exercise.min_user_level,
        last_code=progress.last_code if progress else exercise.starter_code,
        solved=progress.status == ProgressStatus.SOLVED if progress else False,
    )


@router.post("/{exercise_id}/submit", response_model=SubmitCodeResponse)
def submit_exercise(
    exercise_id: int,
    payload: SubmitCodeRequest,
    user_id: int = Depends(resolve_user_id),
    db: Session = Depends(get_db),
) -> SubmitCodeResponse:
    user = get_default_user(db, user_id)
    exercise = _get_exercise_or_404(db, exercise_id)

    if not is_level_available(user.level, exercise.min_user_level):
        raise HTTPException(status_code=403, detail="Задание недоступно на вашем уровне")

    try:
        result = run_user_code(payload.code, exercise.function_name, exercise.tests_json)
    except CodeValidationError as exc:
        return SubmitCodeResponse(
            success=False,
            stdout="",
            stderr="",
            tests=[],
            error=str(exc),
        )

    upsert_progress(db, user_id, exercise_id, payload.code, result.success)
    return result


@router.get("/{exercise_id}/hint", response_model=HintResponse)
def get_hint(
    exercise_id: int,
    user_id: int = Depends(resolve_user_id),
    db: Session = Depends(get_db),
) -> HintResponse:
    user = get_default_user(db, user_id)
    exercise = _get_exercise_or_404(db, exercise_id)

    if not is_level_available(user.level, exercise.min_user_level):
        raise HTTPException(status_code=403, detail="Задание недоступно на вашем уровне")

    return HintResponse(hint=exercise.hint)


@router.get("/{exercise_id}/solution", response_model=SolutionResponse)
def get_solution(
    exercise_id: int,
    user_id: int = Depends(resolve_user_id),
    db: Session = Depends(get_db),
) -> SolutionResponse:
    user = get_default_user(db, user_id)
    exercise = _get_exercise_or_404(db, exercise_id)

    if not is_level_available(user.level, exercise.min_user_level):
        raise HTTPException(status_code=403, detail="Задание недоступно на вашем уровне")

    return SolutionResponse(
        solution=exercise.solution,
        explanation=exercise.solution_explanation,
    )
