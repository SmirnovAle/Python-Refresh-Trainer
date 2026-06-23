# Python Refresh Trainer

Личный веб-тренажёр для повторения встроенных возможностей Python.

## Стек

- Backend: FastAPI + SQLite
- Frontend: React + Vite
- Python runner: 3.12, subprocess, timeout 2s
- Deploy: Docker Compose + nginx

## Быстрый старт

### Локально (без входа)

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Открыть: http://localhost:8080 — auth отключён (`TRAINER_AUTH_ENABLED=false`).

### VPS (вход в приложении)

```bash
export TRAINER_JWT_SECRET=$(openssl rand -hex 32)
export TRAINER_ADMIN_PASSWORD='ваш_пароль'
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

Логин: **admin@local** / пароль из `TRAINER_ADMIN_PASSWORD`. JWT в httpOnly-cookie.

## Уровни пользователя

- Начальный
- Средний
- Продвинутый
- Эксперт

Уровень фильтрует доступные темы и задания. Прогресс — % решённых задач от доступных на текущем уровне.

## MVP контент

18 тем, **62 задания** с теорией, подсказками, эталонными решениями и разбором инструментов.

## API

- `GET /api/health` — без auth
- `POST /api/auth/login` — вход, JWT-cookie
- `POST /api/auth/logout`
- `GET /api/users/me`
- `PATCH /api/users/me/level`
- `GET /api/topics`
- `GET /api/topics/{slug}`
- `GET /api/exercises/{id}`
- `POST /api/exercises/{id}/submit`
- `GET /api/exercises/{id}/hint`
- `GET /api/exercises/{id}/solution`
- `GET /api/progress/summary`
- `POST /api/ai/explain` — разбор ошибки (нужен `TRAINER_AI_ENABLED` + API-ключ)
- `GET /api/ai/status` — включён ли AI

## Деплой на VPS

Приложение на VPS слушает **127.0.0.1:8090** (prod). Локально — `:8080`. Снаружи — nginx + SSL.

### 1. Подготовка VPS (один раз)

```bash
# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# перелогиньтесь

# Клон репозитория
sudo mkdir -p /opt
sudo git clone https://github.com/SmirnovAle/Python-Refresh-Trainer.git /opt/python-refresh-trainer
sudo chown -R $USER:$USER /opt/python-refresh-trainer
cd /opt/python-refresh-trainer

export TRAINER_JWT_SECRET=$(openssl rand -hex 32)
export TRAINER_ADMIN_PASSWORD='ваш_пароль'
```

### 2. Запуск приложения

```bash
cd /opt/python-refresh-trainer
export TRAINER_JWT_SECRET='...'   # сохраните в ~/.bashrc или systemd env
export TRAINER_ADMIN_PASSWORD='...'
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
curl -sf http://127.0.0.1:8090/api/health
```

Или скрипт:

```bash
chmod +x deploy/vps/deploy.sh
APP_DIR=/opt/python-refresh-trainer ./deploy/vps/deploy.sh
```

### 3. Внешний nginx + SSL

```bash
# Замените trainer.example.com на ваш домен в deploy/vps/nginx-site.conf
sudo cp deploy/vps/nginx-site.conf /etc/nginx/sites-available/python-trainer
sudo ln -sf /etc/nginx/sites-available/python-trainer /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

sudo certbot --nginx -d trainer.example.com
```

DNS: A-запись домена → IP VPS.

### 4. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
# 8090 наружу НЕ открываем — доступ только через nginx
```

### 5. Обновление

```bash
cd /opt/python-refresh-trainer
./deploy/vps/update.sh
```

### 6. Бэкап SQLite

```bash
chmod +x deploy/vps/backup-db.sh
./deploy/vps/backup-db.sh
# cron: 0 3 * * * /opt/python-refresh-trainer/deploy/vps/backup-db.sh
```

Бэкапы: `/var/backups/python-trainer/`, хранятся 14 дней.

### Схема

```
Интернет → nginx:443 (SSL) → 127.0.0.1:8090 (docker frontend) → backend:8000
```

Вход — через форму в приложении (JWT-cookie). nginx Basic Auth больше не используется.

### Безопасность

- **HTTPS**: TLS на внешнем nginx (`deploy/vps/nginx-site.conf`), HTTP → 301 на HTTPS, HSTS.
- **Cookie**: `Secure` + `HttpOnly` + `SameSite=Lax` в prod (`TRAINER_COOKIE_SECURE=true`).
- **JWT**: 24 часа (`TRAINER_JWT_EXPIRE_HOURS`).
- **Пароли**: bcrypt, cost factor 12.
- **CORS**: явный список origin (`TRAINER_CORS_ORIGINS`), `credentials: true` — wildcard `*` не используется.

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
| `TRAINER_AUTH_ENABLED` | `true` |
| `TRAINER_ADMIN_EMAIL` | `admin@local` |
| `TRAINER_ADMIN_PASSWORD` | `dev` |
| `TRAINER_JWT_SECRET` | `dev-insecure-change-me` |
| `TRAINER_JWT_EXPIRE_HOURS` | `24` |
| `TRAINER_COOKIE_SECURE` | `false` |
| `TRAINER_CORS_ORIGINS` | `http://localhost:8080,http://localhost:5173` |
| `TRAINER_AI_ENABLED` | `false` |
| `TRAINER_OPENAI_API_KEY` | — |
| `TRAINER_AI_MODEL` | `gpt-4o-mini` |
| `TRAINER_AI_BASE_URL` | `https://api.openai.com/v1` |
| `TRAINER_AI_TIMEOUT_SECONDS` | `30.0` |

### AI (опционально)

```bash
export TRAINER_AI_ENABLED=true
export TRAINER_OPENAI_API_KEY='sk-...'
# для совместимых API (OpenRouter, локальный proxy):
# export TRAINER_AI_BASE_URL='https://openrouter.ai/api/v1'
# export TRAINER_AI_MODEL='...'
```
