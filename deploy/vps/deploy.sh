#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/python-refresh-trainer}"
REPO_URL="${REPO_URL:-https://github.com/SmirnovAle/Python-Refresh-Trainer.git}"
COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"

echo "==> Python Refresh Trainer — деплой в ${APP_DIR}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker не установлен. Установите Docker и docker-compose."
  exit 1
fi

if [ ! -d "${APP_DIR}/.git" ]; then
  sudo mkdir -p "$(dirname "${APP_DIR}")"
  sudo git clone "${REPO_URL}" "${APP_DIR}"
  sudo chown -R "${USER}:${USER}" "${APP_DIR}"
else
  cd "${APP_DIR}"
  git pull --ff-only
fi

cd "${APP_DIR}"

if [ ! -f nginx/.htpasswd ]; then
  echo "Создайте nginx/.htpasswd:"
  echo "  htpasswd -nbB admin 'YOUR_PASSWORD' | sudo tee nginx/.htpasswd"
  exit 1
fi

chmod 644 nginx/.htpasswd 2>/dev/null || sudo chmod 644 nginx/.htpasswd

echo "==> Сборка и запуск контейнеров"
${COMPOSE} up --build -d

echo "==> Проверка"
sleep 3
curl -sf http://127.0.0.1:8090/api/health >/dev/null \
  && echo "OK: приложение отвечает на 127.0.0.1:8090" \
  || echo "WARN: health-check не прошёл — проверьте логи: ${COMPOSE} logs"

echo
echo "Дальше:"
echo "  1. Настройте внешний nginx: deploy/vps/nginx-site.conf"
echo "  2. sudo certbot --nginx -d YOUR_DOMAIN"
echo "  3. ufw allow 80,443 && ufw enable  (порт 8080 наружу не открывать)"
