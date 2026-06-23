import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExerciseDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProgressStatus(str, enum.Enum):
    ATTEMPTED = "attempted"
    SOLVED = "solved"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    level: Mapped[UserLevel] = mapped_column(Enum(UserLevel), default=UserLevel.BEGINNER)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    progress: Mapped[list["Progress"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    theory_md: Mapped[str] = mapped_column(Text, nullable=False)
    min_user_level: Mapped[UserLevel] = mapped_column(Enum(UserLevel), default=UserLevel.BEGINNER)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    exercises: Mapped[list["Exercise"]] = relationship(back_populates="topic")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    hint: Mapped[str] = mapped_column(Text, nullable=False)
    hint_signature: Mapped[str] = mapped_column(Text, nullable=False, default="")
    solution: Mapped[str] = mapped_column(Text, nullable=False)
    solution_explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    function_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tests_json: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[ExerciseDifficulty] = mapped_column(Enum(ExerciseDifficulty), default=ExerciseDifficulty.EASY)
    min_user_level: Mapped[UserLevel] = mapped_column(Enum(UserLevel), default=UserLevel.BEGINNER)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    topic: Mapped["Topic"] = relationship(back_populates="exercises")
    progress_entries: Mapped[list["Progress"]] = relationship(back_populates="exercise")


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("user_id", "exercise_id", name="uq_user_exercise"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)
    status: Mapped[ProgressStatus] = mapped_column(Enum(ProgressStatus), default=ProgressStatus.ATTEMPTED)
    last_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="progress")
    exercise: Mapped["Exercise"] = relationship(back_populates="progress_entries")
