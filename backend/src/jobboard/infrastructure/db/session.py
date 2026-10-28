from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from jobboard.config import get_settings


def create_database_engine(database_url: str | None = None) -> Engine:
    return create_engine(
        database_url or get_settings().database_url,
        pool_pre_ping=True,
    )


engine = create_database_engine()
SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    with SessionFactory() as session:
        yield session
