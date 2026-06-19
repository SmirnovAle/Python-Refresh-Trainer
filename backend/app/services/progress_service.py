from sqlalchemy.orm import Session

from app.models import Exercise, Progress, ProgressStatus, User, UserLevel

LEVEL_ORDER = [
    UserLevel.BEGINNER,
    UserLevel.INTERMEDIATE,
    UserLevel.ADVANCED,
    UserLevel.EXPERT,
]


def level_rank(level: UserLevel) -> int:
    return LEVEL_ORDER.index(level)


def is_level_available(user_level: UserLevel, required_level: UserLevel) -> bool:
    return level_rank(user_level) >= level_rank(required_level)


def get_default_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise LookupError("Пользователь не найден")
    return user


def available_exercises_query(db: Session, user: User):
    return db.query(Exercise).filter(
        Exercise.min_user_level.in_(
            [level for level in UserLevel if is_level_available(user.level, level)]
        )
    )


def get_progress_summary(db: Session, user: User) -> dict[str, int | float]:
    available = available_exercises_query(db, user).all()
    available_ids = {item.id for item in available}

    solved_rows = (
        db.query(Progress)
        .filter(
            Progress.user_id == user.id,
            Progress.status == ProgressStatus.SOLVED,
            Progress.exercise_id.in_(available_ids),
        )
        .all()
    )
    solved_count = len(solved_rows)
    total = len(available_ids)
    percent = round((solved_count / total) * 100, 1) if total else 0.0

    return {
        "total_available": total,
        "solved_count": solved_count,
        "percent": percent,
    }


def get_solved_exercise_ids(db: Session, user_id: int) -> set[int]:
    rows = (
        db.query(Progress.exercise_id)
        .filter(
            Progress.user_id == user_id,
            Progress.status == ProgressStatus.SOLVED,
        )
        .all()
    )
    return {row[0] for row in rows}


def upsert_progress(
    db: Session,
    user_id: int,
    exercise_id: int,
    code: str,
    solved: bool,
) -> None:
    progress = (
        db.query(Progress)
        .filter(
            Progress.user_id == user_id,
            Progress.exercise_id == exercise_id,
        )
        .first()
    )
    status = ProgressStatus.SOLVED if solved else ProgressStatus.ATTEMPTED

    if progress is None:
        progress = Progress(
            user_id=user_id,
            exercise_id=exercise_id,
            status=status,
            last_code=code,
        )
        db.add(progress)
    else:
        progress.status = status if solved else progress.status
        progress.last_code = code
        if solved:
            progress.status = ProgressStatus.SOLVED

    db.commit()
