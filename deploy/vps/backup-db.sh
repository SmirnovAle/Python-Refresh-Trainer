#!/usr/bin/env bash
# Ежедневный бэкап SQLite volume
# crontab: 0 3 * * * /opt/python-refresh-trainer/deploy/vps/backup-db.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/python-refresh-trainer}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/python-trainer}"
VOLUME="${VOLUME:-python-refresh-trainer_trainer_data}"
KEEP_DAYS="${KEEP_DAYS:-14}"

mkdir -p "${BACKUP_DIR}"
STAMP=$(date +%Y%m%d_%H%M%S)
TARGET="${BACKUP_DIR}/trainer_${STAMP}.db"

docker run --rm \
  -v "${VOLUME}:/data:ro" \
  -v "${BACKUP_DIR}:/backup" \
  alpine cp /data/trainer.db "/backup/trainer_${STAMP}.db"

find "${BACKUP_DIR}" -name 'trainer_*.db' -mtime +"${KEEP_DAYS}" -delete
echo "OK: ${TARGET}"
