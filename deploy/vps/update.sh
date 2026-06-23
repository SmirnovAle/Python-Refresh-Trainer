#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/python-refresh-trainer}"
ENV_FILE="${APP_DIR}/.deploy.env"

cd "${APP_DIR}"
sudo git fetch origin main
sudo git reset --hard origin/main

if [ -f "$ENV_FILE" ]; then
  TRAINER_JWT_SECRET=$(sudo grep '^TRAINER_JWT_SECRET=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r')
  TRAINER_ADMIN_PASSWORD=$(sudo grep '^TRAINER_ADMIN_PASSWORD=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r')
  TRAINER_AI_ENABLED=$(sudo grep '^TRAINER_AI_ENABLED=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r' || true)
  TRAINER_OPENAI_API_KEY=$(sudo grep '^TRAINER_OPENAI_API_KEY=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r' || true)
  TRAINER_AI_MODEL=$(sudo grep '^TRAINER_AI_MODEL=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r' || true)
  TRAINER_AI_FALLBACK_MODELS=$(sudo grep '^TRAINER_AI_FALLBACK_MODELS=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r' || true)
  TRAINER_AI_BASE_URL=$(sudo grep '^TRAINER_AI_BASE_URL=' "$ENV_FILE" | cut -d= -f2- | tr -d '\r' || true)
else
  echo "Нет ${ENV_FILE}. Запустите deploy/vps/deploy.sh или создайте файл вручную."
  exit 1
fi

export TRAINER_CORS_ORIGINS="${TRAINER_CORS_ORIGINS:-https://python-simulator.ai-smirnov.ru}"
export TRAINER_AI_ENABLED="${TRAINER_AI_ENABLED:-false}"

DEPLOY_ENV=(
  "TRAINER_JWT_SECRET=$TRAINER_JWT_SECRET"
  "TRAINER_ADMIN_PASSWORD=$TRAINER_ADMIN_PASSWORD"
  "TRAINER_CORS_ORIGINS=$TRAINER_CORS_ORIGINS"
  "TRAINER_AI_ENABLED=$TRAINER_AI_ENABLED"
)

if [ -n "${TRAINER_OPENAI_API_KEY:-}" ]; then
  DEPLOY_ENV+=("TRAINER_OPENAI_API_KEY=$TRAINER_OPENAI_API_KEY")
fi
if [ -n "${TRAINER_AI_MODEL:-}" ]; then
  DEPLOY_ENV+=("TRAINER_AI_MODEL=$TRAINER_AI_MODEL")
fi
if [ -n "${TRAINER_AI_FALLBACK_MODELS:-}" ]; then
  DEPLOY_ENV+=("TRAINER_AI_FALLBACK_MODELS=$TRAINER_AI_FALLBACK_MODELS")
fi
if [ -n "${TRAINER_AI_BASE_URL:-}" ]; then
  DEPLOY_ENV+=("TRAINER_AI_BASE_URL=$TRAINER_AI_BASE_URL")
fi

sudo "${DEPLOY_ENV[@]}" docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

sudo "${DEPLOY_ENV[@]}" docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

sudo "${DEPLOY_ENV[@]}" docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
