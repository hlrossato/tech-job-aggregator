from datetime import UTC, datetime
from uuid import uuid4

from jobboard.domain.models import JobView, WorkplaceType


def make_job(**overrides: object) -> JobView:
    values: dict[str, object] = {
        "id": uuid4(),
        "title": "Senior Python Engineer",
        "company_name": "Northwind Labs",
        "description": "Python, FastAPI and PostgreSQL",
        "canonical_url": "https://example.com/jobs/python",
        "apply_url": "https://example.com/jobs/python",
        "location_text": "Remote, Brazil",
        "country_code": "BR",
        "workplace_type": WorkplaceType.REMOTE,
        "employment_type": "full-time",
        "seniority": "senior",
        "salary_min": None,
        "salary_max": None,
        "salary_currency": None,
        "technologies": ("Python", "PostgreSQL"),
        "role_category": "software-engineering",
        "published_at": datetime(2026, 10, 1, tzinfo=UTC),
        "first_seen_at": datetime(2026, 10, 1, tzinfo=UTC),
        "source_name": "Demo source",
        "source_url": "https://example.com/jobs",
    }
    values.update(overrides)
    return JobView(**values)  # type: ignore[arg-type]
