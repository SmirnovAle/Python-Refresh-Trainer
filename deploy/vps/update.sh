#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/python-refresh-trainer}"
ENV_FILE="${APP_DIR}/.deploy.env"

cd "${APP_DIR}"
sudo git fetch origin main
sudo git reset --hard origin/main

if [ -f "$ENV_FILE" ]; then
  TRAINER_JWT_SECRET=$(sudo grep '^TRAINER_JWT_SECRET=' "$ENV_FILE" | cut -d= -f2-)
  TRAINER_ADMIN_PASSWORD=$(sudo grep '^TRAINER_ADMIN_PASSWORD=' "$ENV_FILE" | cut -d= -f2-)
else
  echo "Нет ${ENV_FILE}. Запустите deploy/vps/deploy.sh или создайте файл вручную."
  exit 1
fi

export TRAINER_CORS_ORIGINS="${TRAINER_CORS_ORIGINS:-https://python-simulator.ai-smirnov.ru}"

sudo TRAINER_JWT_SECRET="$TRAINER_JWT_SECRET" \
  TRAINER_ADMIN_PASSWORD="$TRAINER_ADMIN_PASSWORD" \
  TRAINER_CORS_ORIGINS="$TRAINER_CORS_ORIGINS" \
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

sudo TRAINER_JWT_SECRET="$TRAINER_JWT_SECRET" \
  TRAINER_ADMIN_PASSWORD="$TRAINER_ADMIN_PASSWORD" \
  TRAINER_CORS_ORIGINS="$TRAINER_CORS_ORIGINS" \
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
