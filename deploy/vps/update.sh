#!/usr/bin/env bash
# Обновление уже развёрнутого приложения
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/python-refresh-trainer}"
COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"

cd "${APP_DIR}"
git pull --ff-only
${COMPOSE} up --build -d
${COMPOSE} ps
