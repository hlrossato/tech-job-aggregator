# Technology Jobs Aggregator

A privacy-friendly search engine for public technology jobs. There are no accounts, no email capture, and no in-site applications. Search, filter, then apply on the original posting.

## Stack

- React + TypeScript + Vite
- FastAPI + Pydantic
- PostgreSQL + SQLAlchemy + Alembic
- Scrapy crawlers for public ATS feeds and Schema.org `JobPosting` pages
- Cron or systemd timers

## Run with Docker

This starts Postgres, applies migrations, and serves the API and frontend:

```bash
docker compose up --build
```

Open http://localhost:5173. Seed demo jobs from the API image, then search:

```bash
docker compose run --rm api python /app/scripts/seed_demo.py
```

Enabled sources can be crawled without a host virtualenv. Sources in `backend/sources.toml` stay disabled until you review them, and that file is mounted into the crawler so a change does not require a rebuild:

```bash
docker compose --profile crawler run --rm crawler
```

Production uses the same images with [compose.prod.yml](compose.prod.yml). See [deploy/README.md](deploy/README.md).

## Local development

Use this when you want reload on each edit. Rebuilding images on every change is slow.

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
