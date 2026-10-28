# Deployment

The MVP is provider-neutral. Run PostgreSQL, the FastAPI API, scheduled crawls, and a static frontend behind HTTPS.

## Release

1. Apply migrations explicitly: `cd backend && uv run alembic upgrade head`
2. Build and restart the API
3. Build the frontend with `VITE_API_URL=/api/v1` if nginx proxies `/api`
4. Confirm `/health` and `/ready`

## Scheduling

Use `deploy/crontab.example` or `deploy/jobboard-crawl.service` plus `jobboard-crawl.timer`.
The crawl script refuses overlapping runs through `backend/.crawl-lock`.

## Backups

`scripts/backup_db.sh` writes compressed `pg_dump` files. Retain at least 7 daily copies.

## Monitoring

`scripts/check_health.sh` fails if the API is down. Watch:

- crawl success/failure from `crawl_runs`
- stale apply links
- search latency and zero-result searches in API logs
- outbound apply clicks in access logs
