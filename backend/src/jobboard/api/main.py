import logging

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from jobboard.api.dependencies import SessionDependency
from jobboard.api.routes.jobs import router as jobs_router
from jobboard.api.schemas import HealthResponse
from jobboard.config import get_settings

settings = get_settings()
logging.basicConfig(level=settings.log_level)
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(jobs_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse, tags=["operations"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/ready", response_model=HealthResponse, tags=["operations"])
def readiness(session: SessionDependency) -> HealthResponse:
    session.execute(text("SELECT 1"))
    return HealthResponse(status="ready")
