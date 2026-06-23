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
    email: str | None = None
    level: UserLevel

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class AuthConfigResponse(BaseModel):
    registration_enabled: bool


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
    hint_signature: str = ""


class SolutionResponse(BaseModel):
    solution: str
    explanation: str


class AiExplainRequest(BaseModel):
    exercise_id: int
    code: str = Field(min_length=1)
    error: str | None = None
    stderr: str | None = None
    failed_tests: list[str] = Field(default_factory=list)


class AiExplainResponse(BaseModel):
    explanation: str
    model: str


class HealthResponse(BaseModel):
    status: str
    python_version: str
