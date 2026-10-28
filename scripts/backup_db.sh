#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/jobboard}"
DATABASE_URL="${DATABASE_URL:-postgresql://jobboard:jobboard@localhost:5432/jobboard}"
mkdir -p "$BACKUP_DIR"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
pg_dump "$DATABASE_URL" | gzip > "$BACKUP_DIR/jobboard-$stamp.sql.gz"
find "$BACKUP_DIR" -name 'jobboard-*.sql.gz' -mtime +7 -delete
echo "wrote $BACKUP_DIR/jobboard-$stamp.sql.gz"
