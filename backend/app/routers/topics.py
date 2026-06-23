from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Exercise, Topic
from app.dependencies.auth import require_user_id
from app.schemas import ExerciseSummary, TopicDetail, TopicSummary
from app.services.progress_service import (
    get_default_user,
    get_solved_exercise_ids,
    is_level_available,
)

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=list[TopicSummary])
def list_topics(
    user_id: int = Depends(require_user_id),
    db: Session = Depends(get_db),
) -> list[TopicSummary]:
    user = get_default_user(db, user_id)
    solved_ids = get_solved_exercise_ids(db, user_id)
    topics = db.query(Topic).order_by(Topic.sort_order).all()
    result: list[TopicSummary] = []

    for topic in topics:
        exercises = [
            exercise
            for exercise in topic.exercises
            if is_level_available(user.level, exercise.min_user_level)
        ]
        available = is_level_available(user.level, topic.min_user_level)
        solved_count = sum(1 for exercise in exercises if exercise.id in solved_ids)

        result.append(
            TopicSummary(
                id=topic.id,
                slug=topic.slug,
                title=topic.title,
                min_user_level=topic.min_user_level,
                sort_order=topic.sort_order,
                exercise_count=len(exercises),
                solved_count=solved_count,
                available=available,
            )
        )

    return result


@router.get("/{slug}", response_model=TopicDetail)
def get_topic(
    slug: str,
    user_id: int = Depends(require_user_id),
    db: Session = Depends(get_db),
) -> TopicDetail:
    user = get_default_user(db, user_id)
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    if not is_level_available(user.level, topic.min_user_level):
        raise HTTPException(status_code=403, detail="Тема недоступна на вашем уровне")

    solved_ids = get_solved_exercise_ids(db, user_id)
    exercises = [
        ExerciseSummary(
            id=exercise.id,
            title=exercise.title,
            difficulty=exercise.difficulty,
            min_user_level=exercise.min_user_level,
            sort_order=exercise.sort_order,
            solved=exercise.id in solved_ids,
        )
        for exercise in sorted(topic.exercises, key=lambda item: item.sort_order)
        if is_level_available(user.level, exercise.min_user_level)
    ]

    return TopicDetail(
        id=topic.id,
        slug=topic.slug,
        title=topic.title,
        theory_md=topic.theory_md,
        min_user_level=topic.min_user_level,
        exercises=exercises,
    )
