# Python Refresh Trainer

Личный веб-тренажёр для повторения встроенных возможностей Python.

## Стек

- Backend: FastAPI + SQLite
- Frontend: React + Vite
- Python runner: 3.12, subprocess, timeout 2s
- Deploy: Docker Compose + nginx

## Быстрый старт

### Локально (без пароля)

```bash
docker-compose up --build
```

Открыть: http://localhost:8080

### VPS (Basic Auth до пользовательских аккаунтов)

```bash
docker run --rm httpd:2.4-alpine htpasswd -nbB admin YOUR_PASSWORD > nginx/.htpasswd
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

Логин/пароль — из `.htpasswd`. После реализации auth в приложении убрать `docker-compose.prod.yml`.

## Уровни пользователя

- Начальный
- Средний
- Продвинутый
- Эксперт

Уровень фильтрует доступные темы и задания. Прогресс — % решённых задач от доступных на текущем уровне.

## MVP контент

Полные задания: strings, lists, dictionaries, comprehensions.

Остальные темы — теория-заглушка, задания позже.

## API

- `GET /api/health`
- `GET /api/users/me`
- `PATCH /api/users/me/level`
- `GET /api/topics`
- `GET /api/topics/{slug}`
- `GET /api/exercises/{id}`
- `POST /api/exercises/{id}/submit`
- `GET /api/exercises/{id}/hint`
- `GET /api/exercises/{id}/solution`
- `GET /api/progress/summary`
- `POST /api/ai/explain` — заглушка (501)

## Деплой на VPS с nginx

1. Сгенерировать `nginx/.htpasswd` и запустить с prod-override:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

2. Проксировать домен через внешний nginx:

```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

3. SSL через certbot.

## Локальная разработка без Docker

```bash
# backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm run dev
```

## Переменные окружения backend

| Переменная | По умолчанию |
|------------|--------------|
| `TRAINER_DATABASE_URL` | `sqlite:///./data/trainer.db` |
| `TRAINER_DEFAULT_USER_ID` | `1` |
| `TRAINER_CODE_TIMEOUT_SECONDS` | `2.0` |
