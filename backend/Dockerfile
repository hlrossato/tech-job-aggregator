FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY src src
RUN pip install --no-cache-dir .
COPY migrations migrations
COPY alembic.ini ./
COPY scrapy.cfg ./

ENV PYTHONPATH=/app/src
CMD ["uvicorn", "jobboard.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
