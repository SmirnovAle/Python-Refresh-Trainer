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

13 тем, **39 заданий** с теорией, подсказками, эталонными решениями и разбором инструментов.

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

## Деплой на VPS

Приложение слушает **только localhost:8080**. Снаружи — ваш nginx + SSL.

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

# Basic Auth (до пользовательских аккаунтов)
docker run --rm httpd:2.4-alpine htpasswd -nbB admin 'ВАШ_ПАРОЛЬ' > nginx/.htpasswd
chmod 600 nginx/.htpasswd
```

### 2. Запуск приложения

```bash
cd /opt/python-refresh-trainer
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
curl -u admin:ВАШ_ПАРОЛЬ http://127.0.0.1:8080/api/health
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
# 8080 наружу НЕ открываем — доступ только через nginx
```

### 5. Обновление

```bash
cd /opt/python-refresh-trainer
./deploy/vps/update.sh
```

### Схема

```
Интернет → nginx:443 (SSL) → 127.0.0.1:8080 (docker frontend + Basic Auth) → backend:8000
```

После реализации auth в приложении уберите `docker-compose.prod.yml` и Basic Auth из `nginx/nginx.prod.conf`.

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
