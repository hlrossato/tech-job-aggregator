.PHONY: install test lint migrate api crawl frontend

install:
	cd backend && uv sync --dev

test:
	cd backend && uv run pytest --cov=jobboard

lint:
	cd backend && uv run ruff check src tests && uv run mypy src

migrate:
	cd backend && uv run alembic upgrade head

api:
	cd backend && uv run uvicorn jobboard.api.main:app --reload

crawl:
	cd backend && uv run scrapy crawl $(SPIDER) -a board=$(BOARD)

frontend:
	cd frontend && npm run dev
