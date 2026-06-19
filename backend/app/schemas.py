from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class UserLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExerciseDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProgressStatus(str, Enum):
    ATTEMPTED = "attempted"
    SOLVED = "solved"


USER_LEVEL_LABELS: dict[UserLevel, str] = {
    UserLevel.BEGINNER: "Начальный",
    UserLevel.INTERMEDIATE: "Средний",
    UserLevel.ADVANCED: "Продвинутый",
    UserLevel.EXPERT: "Эксперт",
}

DIFFICULTY_LABELS: dict[ExerciseDifficulty, str] = {
    ExerciseDifficulty.EASY: "Лёгкое",
    ExerciseDifficulty.MEDIUM: "Среднее",
    ExerciseDifficulty.HARD: "Сложное",
}


class UserOut(BaseModel):
    id: int
    name: str
    level: UserLevel

    model_config = {"from_attributes": True}


class UserLevelUpdate(BaseModel):
    level: UserLevel


class ExerciseSummary(BaseModel):
    id: int
    title: str
    difficulty: ExerciseDifficulty
    min_user_level: UserLevel
    sort_order: int
    solved: bool = False

    model_config = {"from_attributes": True}


class TopicSummary(BaseModel):
    id: int
    slug: str
    title: str
    min_user_level: UserLevel
    sort_order: int
    exercise_count: int
    solved_count: int
    available: bool

    model_config = {"from_attributes": True}


class TopicDetail(BaseModel):
    id: int
    slug: str
    title: str
    theory_md: str
    min_user_level: UserLevel
    exercises: list[ExerciseSummary]

    model_config = {"from_attributes": True}


class ExerciseDetail(BaseModel):
    id: int
    topic_id: int
    topic_slug: str
    topic_title: str
    title: str
    description: str
    starter_code: str
    hint: str
    solution: str
    function_name: str
    difficulty: ExerciseDifficulty
    min_user_level: UserLevel
    last_code: str | None = None
    solved: bool = False

    model_config = {"from_attributes": True}


class ProgressSummary(BaseModel):
    total_available: int
    solved_count: int
    percent: float


class SubmitCodeRequest(BaseModel):
    code: str = Field(min_length=1)


class TestResult(BaseModel):
    index: int
    passed: bool
    message: str


class SubmitCodeResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str
    tests: list[TestResult]
    error: str | None = None


class HintResponse(BaseModel):
    hint: str


class SolutionResponse(BaseModel):
    solution: str


class AiExplainRequest(BaseModel):
    code: str
    error: str | None = None


class AiExplainResponse(BaseModel):
    explanation: str


class HealthResponse(BaseModel):
    status: str
    python_version: str
