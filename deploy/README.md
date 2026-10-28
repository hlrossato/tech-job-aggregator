# Deployment

Run the same images used locally, on a single host, with Compose. Clone the repo, create an untracked `.env`, and start the stack. There is no image registry in this setup.

## Environment

Copy `.env.example` to `.env` and set a real `POSTGRES_PASSWORD`. Use a URL-safe password so it can sit in `DATABASE_URL`. `POSTGRES_USER` and `POSTGRES_DB` default to `jobboard` when unset.

`API_CORS_ORIGINS` is a JSON list. The frontend calls `/api` on the same host, so the browser does not depend on that list for normal search. Set it to the public origin if a client calls the API directly.

Do not run `scripts/seed_demo.py` on a production database.

## Release

TLS terminates in front of these containers. Put Caddy or a host reverse proxy on the public interface and forward it to the frontend on port 80. Leave Postgres on the Compose network only. The production file publishes no database or API port.

```bash
docker compose -f compose.yml -f compose.prod.yml up -d --build
```

The API entrypoint runs `alembic upgrade head` before uvicorn. One API container is enough. Confirm `http://127.0.0.1/health` and `http://127.0.0.1/ready` through nginx.

## Scheduling

Use `deploy/crontab.example` or `deploy/jobboard-crawl.service` plus `jobboard-crawl.timer`.
Both invoke:

```bash
docker compose -f compose.yml -f compose.prod.yml run --rm crawler
```

`backend/sources.toml` is mounted into the crawler. Enable a source there after you review its terms, `robots.txt`, and rate limits. The crawl script refuses overlapping runs through `backend/.crawl-lock` inside the container.

Expire jobs the same way, replacing `demo` with a real source key:

```bash
docker compose -f compose.yml -f compose.prod.yml run --rm api \
  python /app/scripts/expire_unseen.py demo --hours 48
```

## Backups

`scripts/backup_db.sh` writes compressed `pg_dump` files and deletes copies older than 7 days. On the server set `BACKUP_VIA_DOCKER=1` so the dump runs inside the database container. The direct `pg_dump "$DATABASE_URL"` path remains for a database that is not in Compose.

## Monitoring

`scripts/check_health.sh` fails if `/health` or `/ready` is down. Point it at nginx:

```bash
HEALTHCHECK_URL=http://127.0.0.1 ./scripts/check_health.sh
```

Also watch:

- crawl success/failure from `crawl_runs`
- stale apply links
- search latency and zero-result searches in API logs
- outbound apply clicks in access logs
