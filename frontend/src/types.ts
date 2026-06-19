export type UserLevel = "beginner" | "intermediate" | "advanced" | "expert";
export type ExerciseDifficulty = "easy" | "medium" | "hard";

export interface User {
  id: number;
  name: string;
  level: UserLevel;
}

export interface ProgressSummary {
  total_available: number;
  solved_count: number;
  percent: number;
}

export interface TopicSummary {
  id: number;
  slug: string;
  title: string;
  min_user_level: UserLevel;
  sort_order: number;
  exercise_count: number;
  solved_count: number;
  available: boolean;
}

export interface ExerciseSummary {
  id: number;
  title: string;
  difficulty: ExerciseDifficulty;
  min_user_level: UserLevel;
  sort_order: number;
  solved: boolean;
}

export interface TopicDetail {
  id: number;
  slug: string;
  title: string;
  theory_md: string;
  min_user_level: UserLevel;
  exercises: ExerciseSummary[];
}

export interface ExerciseDetail {
  id: number;
  topic_id: number;
  topic_slug: string;
  topic_title: string;
  title: string;
  description: string;
  starter_code: string;
  hint: string;
  solution: string;
  function_name: string;
  difficulty: ExerciseDifficulty;
  min_user_level: UserLevel;
  last_code: string | null;
  solved: boolean;
}

export interface TestResult {
  index: number;
  passed: boolean;
  message: string;
}

export interface SubmitCodeResponse {
  success: boolean;
  stdout: string;
  stderr: string;
  tests: TestResult[];
  error: string | null;
}

export const USER_LEVEL_LABELS: Record<UserLevel, string> = {
  beginner: "Начальный",
  intermediate: "Средний",
  advanced: "Продвинутый",
  expert: "Эксперт",
};

export const DIFFICULTY_LABELS: Record<ExerciseDifficulty, string> = {
  easy: "Лёгкое",
  medium: "Среднее",
  hard: "Сложное",
};
