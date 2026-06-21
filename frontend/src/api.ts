import type {
  ExerciseDetail,
  ProgressSummary,
  SubmitCodeResponse,
  TopicDetail,
  TopicSummary,
  User,
  UserLevel,
} from "./types";

const API_BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = payload.detail ?? response.statusText;
    throw new Error(typeof detail === "string" ? detail : "Ошибка запроса");
  }

  return response.json() as Promise<T>;
}

export function getCurrentUser(): Promise<User> {
  return request<User>("/users/me");
}

export function updateUserLevel(level: UserLevel): Promise<User> {
  return request<User>("/users/me/level", {
    method: "PATCH",
    body: JSON.stringify({ level }),
  });
}

export function getProgressSummary(): Promise<ProgressSummary> {
  return request<ProgressSummary>("/progress/summary");
}

export function getTopics(): Promise<TopicSummary[]> {
  return request<TopicSummary[]>("/topics");
}

export function getTopic(slug: string): Promise<TopicDetail> {
  return request<TopicDetail>(`/topics/${slug}`);
}

export function getExercise(id: number): Promise<ExerciseDetail> {
  return request<ExerciseDetail>(`/exercises/${id}`);
}

export function submitExercise(id: number, code: string): Promise<SubmitCodeResponse> {
  return request<SubmitCodeResponse>(`/exercises/${id}/submit`, {
    method: "POST",
    body: JSON.stringify({ code }),
  });
}

export function getHint(id: number): Promise<{ hint: string }> {
  return request<{ hint: string }>(`/exercises/${id}/hint`);
}

export function getSolution(id: number): Promise<{ solution: string; explanation: string }> {
  return request<{ solution: string; explanation: string }>(`/exercises/${id}/solution`);
}
