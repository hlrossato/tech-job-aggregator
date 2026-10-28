FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

WORKDIR /app/backend

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/backend/.venv

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY backend/src ./src
COPY backend/migrations ./migrations
COPY backend/alembic.ini backend/scrapy.cfg backend/sources.toml ./
COPY backend/docker-entrypoint.sh /app/backend/docker-entrypoint.sh
COPY scripts /app/scripts

RUN uv sync --frozen --no-dev \
    && chmod 755 /app/backend/docker-entrypoint.sh \
    && useradd --create-home --uid 10001 app \
    && chown -R app:app /app

ENV PATH="/app/backend/.venv/bin:$PATH" \
    PYTHONPATH="/app/backend/src"

USER app
EXPOSE 8000
ENTRYPOINT ["/app/backend/docker-entrypoint.sh"]
CMD ["api"]
