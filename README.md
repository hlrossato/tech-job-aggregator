# Technology Jobs Aggregator

A privacy-friendly search engine for public technology jobs. There are no accounts, no email capture, and no in-site applications. Search, filter, then apply on the original posting.

## Stack

- React + TypeScript + Vite
- FastAPI + Pydantic
- PostgreSQL + SQLAlchemy + Alembic
- Scrapy crawlers for public ATS feeds and Schema.org `JobPosting` pages
- Cron or systemd timers

## Local development

```bash
cp .env.example .env
docker compose up db -d
cd backend && uv sync --dev && uv run alembic upgrade head
uv run uvicorn jobboard.api.main:app --reload
python ../scripts/seed_demo.py
```

In another terminal:

```bash
cd frontend && npm install && npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` to FastAPI.

## Crawling

Sources live in `backend/sources.toml`. They are disabled until you review terms, `robots.txt`, and rate limits. Enable a source, then:

```bash
python scripts/crawl_sources.py backend/sources.toml
```

Overlapping crawls are blocked by `backend/.crawl-lock`. Jobs not seen after a source-specific grace period are expired.

## Tests

```bash
cd backend && uv run pytest -m "not integration"
cd frontend && npm test
```

PostgreSQL integration tests run when `TEST_DATABASE_URL` is set.

## Production notes

See [deploy/README.md](deploy/README.md) for migrations, HTTPS, backups, crawl scheduling, and health checks.
