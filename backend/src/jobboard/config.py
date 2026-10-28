from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Technology Jobs Aggregator"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://jobboard:jobboard@localhost:5432/jobboard"
    api_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
