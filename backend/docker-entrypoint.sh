#!/bin/sh
set -eu

cd /app/backend

if [ "${1:-}" = "api" ]; then
  alembic upgrade head
  exec uvicorn jobboard.api.main:app --host 0.0.0.0 --port 8000
fi

exec "$@"
