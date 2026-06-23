import httpx

from app.config import settings

RETRYABLE_STATUS_CODES = {429, 502, 503}


class AiServiceError(Exception):
    pass


class AiNotConfiguredError(AiServiceError):
    pass


def _models_to_try() -> list[str]:
    primary = settings.ai_model.strip()
    fallbacks = [item.strip() for item in settings.ai_fallback_models.split(",") if item.strip()]
    seen: set[str] = set()
    models: list[str] = []
    for model in [primary, *fallbacks]:
        if model and model not in seen:
            seen.add(model)
            models.append(model)
    return models


def _request_explanation(
    client: httpx.Client,
    *,
    url: str,
    headers: dict[str, str],
    messages: list[dict[str, str]],
    model: str,
) -> str:
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 600,
    }
    response = client.post(url, headers=headers, json=body)
    response.raise_for_status()
    payload = response.json()
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AiServiceError("Неожиданный формат ответа AI API") from exc
    explanation = content.strip()
    if not explanation:
        raise AiServiceError("AI вернул пустой ответ")
    return explanation


def explain_exercise_failure(
    *,
    title: str,
    description: str,
    function_name: str,
    hint: str,
    code: str,
    error: str | None,
    stderr: str | None,
    failed_tests: list[str],
) -> tuple[str, str]:
    if not settings.ai_enabled:
        raise AiNotConfiguredError("AI отключён. Задайте TRAINER_AI_ENABLED=true")
    if not settings.openai_api_key:
        raise AiNotConfiguredError("AI не настроен. Задайте TRAINER_OPENAI_API_KEY (ключ OpenRouter)")

    user_lines = [
        f"Задание: {title}",
        f"Описание: {description}",
        f"Имя функции: {function_name}",
        f"Подсказка из курса (не цитируй дословно как ответ): {hint}",
        "",
        "Код пользователя:",
        "```python",
        code,
        "```",
    ]

    if error:
        user_lines.extend(["", f"Ошибка выполнения: {error}"])
    if stderr:
        user_lines.extend(["", f"stderr: {stderr}"])
    if failed_tests:
        user_lines.extend(["", "Проваленные автопроверки:"])
        user_lines.extend(f"- {item}" for item in failed_tests)

    messages = [
        {
            "role": "system",
            "content": (
                "Ты помощник в Python-тренажёре. Объясняй ошибки и неверные результаты на русском языке. "
                "Не выдавай полное готовое решение и не переписывай весь код целиком. "
                "Укажи вероятную причину, на что обратить внимание, и один конкретный следующий шаг. "
                "Используй короткие абзацы или маркированный список."
            ),
        },
        {"role": "user", "content": "\n".join(user_lines)},
    ]

    url = f"{settings.ai_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.ai_http_referer,
        "X-Title": settings.ai_app_title,
    }

    models = _models_to_try()
    last_error: Exception | None = None

    try:
        with httpx.Client(timeout=settings.ai_timeout_seconds) as client:
            for model in models:
                try:
                    explanation = _request_explanation(
                        client,
                        url=url,
                        headers=headers,
                        messages=messages,
                        model=model,
                    )
                    return explanation, model
                except httpx.HTTPStatusError as exc:
                    last_error = exc
                    if exc.response.status_code not in RETRYABLE_STATUS_CODES:
                        detail = exc.response.text[:200]
                        raise AiServiceError(
                            f"AI API вернул ошибку {exc.response.status_code}: {detail}"
                        ) from exc
                except httpx.RequestError as exc:
                    last_error = exc
    except AiServiceError:
        raise

    if isinstance(last_error, httpx.HTTPStatusError):
        raise AiServiceError(
            "Бесплатные модели OpenRouter временно перегружены (429). "
            "Подождите минуту и нажмите «Объяснить ошибку» снова."
        ) from last_error
    if isinstance(last_error, httpx.RequestError):
        raise AiServiceError(f"Не удалось связаться с AI API: {last_error}") from last_error

    raise AiServiceError("Не удалось получить ответ AI")
