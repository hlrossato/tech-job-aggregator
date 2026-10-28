.PHONY: install test lint migrate api crawl seed frontend

install:
	cd backend && uv sync --dev
	cd frontend && npm install

test:
	cd backend && uv run pytest -m "not integration" --cov=jobboard
	cd frontend && npm test

lint:
	cd backend && uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy src
	cd frontend && npm run lint

migrate:
	cd backend && uv run alembic upgrade head

api:
	cd backend && uv run uvicorn jobboard.api.main:app --reload

seed:
	python scripts/seed_demo.py

crawl:
	python scripts/crawl_sources.py backend/sources.toml

frontend:
	cd frontend && npm run dev
