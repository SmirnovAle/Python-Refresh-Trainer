# Python Refresh Trainer

Личный веб-тренажёр для повторения встроенных возможностей Python.

## Стек

- Backend: FastAPI + SQLite
- Frontend: React + Vite
- Python runner: 3.12, subprocess, timeout 2s
- Deploy: Docker Compose + nginx

## Быстрый старт (VPS)

Сайт: https://python-simulator.ai-smirnov.ru

```bash
cd /opt/python-refresh-trainer
./deploy/vps/update.sh
```

Логин: **admin@local** / пароль из `/opt/python-refresh-trainer/.deploy.env` (`TRAINER_ADMIN_PASSWORD`).

Первичная установка — раздел [Деплой на VPS](#деплой-на-vps).

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
- `GET /api/auth/config` — включена ли регистрация
- `POST /api/auth/register` — регистрация, JWT-cookie
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

Приложение на VPS слушает **127.0.0.1:8090**. Снаружи — nginx + SSL на домене.

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

## Переменные окружения backend

Задаются в `/opt/python-refresh-trainer/.deploy.env`, подхватываются `deploy/vps/update.sh`.

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
| `TRAINER_COOKIE_SECURE` | `true` (prod) |
| `TRAINER_CORS_ORIGINS` | `https://python-simulator.ai-smirnov.ru` |
| `TRAINER_AI_ENABLED` | `false` |
| `TRAINER_OPENAI_API_KEY` | — (ключ OpenRouter) |
| `TRAINER_AI_MODEL` | `openrouter/free` |
| `TRAINER_AI_FALLBACK_MODELS` | `google/gemma-3-12b-it:free,...` (см. config) |
| `TRAINER_AI_BASE_URL` | `https://openrouter.ai/api/v1` |
| `TRAINER_AI_HTTP_REFERER` | `https://python-simulator.ai-smirnov.ru` |
| `TRAINER_AI_APP_TITLE` | `Python Refresh Trainer` |
| `TRAINER_AI_TIMEOUT_SECONDS` | `45.0` |
| `TRAINER_REGISTRATION_ENABLED` | `true` |
| `TRAINER_MAX_USERS` | `500` |
| `TRAINER_INACTIVE_ACCOUNT_DAYS` | `365` (`0` — не удалять) |

### Пользователи и регистрация

- Регистрация через форму на сайте (`POST /api/auth/register`): имя, email, пароль от 8 символов.
- **Лимит аккаунтов:** `TRAINER_MAX_USERS=500` по умолчанию. Для SQLite на VPS это безопасный запас против спама; технически база выдержит тысячи записей, но прогресс × 62 задания остаётся компактным.
- **Неактивные аккаунты:** при старте backend удаляет пользователей без входа дольше `TRAINER_INACTIVE_ACCOUNT_DAYS` (365 дней). Аккаунт **admin@local** не трогается. `0` — автоочистка выключена.
- Отключить регистрацию: `TRAINER_REGISTRATION_ENABLED=false` в `.deploy.env`.

### AI через OpenRouter (бесплатно)

1. Регистрация: https://openrouter.ai/
2. **Keys** → Create Key (в аккаунте ключ называется `Python-simulator-key`) → скопировать `sk-or-v1-...`
3. На VPS добавить в `/opt/python-refresh-trainer/.deploy.env`:

```bash
TRAINER_AI_ENABLED=true
TRAINER_OPENAI_API_KEY=sk-or-v1-ВАШ_КЛЮЧ
TRAINER_AI_BASE_URL=https://openrouter.ai/api/v1
TRAINER_AI_MODEL=openrouter/free
```

4. Перезапуск: `./deploy/vps/update.sh`

**Рекомендуемая модель:** `openrouter/free` — OpenRouter сам выбирает доступную free-модель; при 429 backend пробует fallback-цепочку.

**Альтернативы (основная модель):**

| Модель | Когда |
|--------|-------|
| `meta-llama/llama-3.3-70b-instruct:free` | лучше качество, но часто 429 |
| `google/gemma-3-12b-it:free` | быстрее, стабильнее |

**Лимиты OpenRouter (free):** 50 запросов/день без пополнения, 20/мин. Отдельные модели могут быть rate-limited у провайдера — тогда сработает fallback или сообщение «подождите минуту».

Проверка: `GET /api/ai/status` → `"configured": true` после деплоя с ключом.
