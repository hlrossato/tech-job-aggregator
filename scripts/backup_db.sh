#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/jobboard}"
DATABASE_URL="${DATABASE_URL:-postgresql://jobboard:jobboard@localhost:5432/jobboard}"
mkdir -p "$BACKUP_DIR"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
outfile="$BACKUP_DIR/jobboard-$stamp.sql.gz"

if [ "${BACKUP_VIA_DOCKER:-0}" = "1" ]; then
  root="$(cd "$(dirname "$0")/.." && pwd)"
  (
    cd "$root"
    docker compose -f compose.yml -f compose.prod.yml exec -T db \
      sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"'
  ) | gzip > "$outfile"
else
  pg_dump "$DATABASE_URL" | gzip > "$outfile"
fi

find "$BACKUP_DIR" -name 'jobboard-*.sql.gz' -mtime +7 -delete
echo "wrote $outfile"
