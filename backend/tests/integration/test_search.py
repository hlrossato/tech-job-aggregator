import os
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from jobboard.application.classification import RuleBasedTechnologyClassifier
from jobboard.application.services import IngestJobService, SearchJobsService
from jobboard.domain.models import JobDraft, JobSearchCriteria, WorkplaceType
from jobboard.infrastructure.db.base import Base
from jobboard.infrastructure.repositories.sqlalchemy import (
    SQLAlchemyJobRepository,
    SQLAlchemyUnitOfWork,
)

pytestmark = pytest.mark.integration

DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture()
def session_factory():
    if not DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL is not set")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        connection.commit()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_upsert_search_and_expire(session_factory) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory)
    service = IngestJobService(uow, RuleBasedTechnologyClassifier())
    draft = JobDraft(
        source_key="itest",
        source_name="Integration",
        source_base_url="https://example.com",
        source_adapter="demo",
        external_id="py-1",
        title="Python Developer",
        company_name="Test Co",
        description="Python FastAPI PostgreSQL",
        canonical_url="https://example.com/jobs/py-1",
        apply_url="https://example.com/jobs/py-1",
        location_text="Brazil",
        workplace_type=WorkplaceType.REMOTE,
        published_at=datetime.now(UTC),
    )
    job_id = service.ingest(draft)
    service.ingest(draft)

    with session_factory() as session:
        search = SearchJobsService(SQLAlchemyJobRepository(session))
        result = search.search(JobSearchCriteria(query="python"))
        assert result.total == 1
        assert result.items[0].id == job_id
        assert "Python" in result.items[0].technologies
        facets = search.facets()
        assert facets.countries.get("BR") == 1
