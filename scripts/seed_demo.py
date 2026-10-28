#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "src"))

from jobboard.application.classification import RuleBasedTechnologyClassifier
from jobboard.application.services import IngestJobService
from jobboard.domain.models import JobDraft, WorkplaceType
from jobboard.infrastructure.repositories.sqlalchemy import SQLAlchemyUnitOfWork

NOW = datetime.now(UTC)
JOBS = [
    JobDraft(
        source_key="demo",
        source_name="Demo source",
        source_base_url="https://example.com/jobs",
        source_adapter="demo",
        external_id="demo-python-1",
        title="Senior Python Engineer",
        company_name="Northwind Labs",
        description="Build APIs with Python, FastAPI, Docker and PostgreSQL. Remote-friendly.",
        canonical_url="https://example.com/jobs/python-engineer",
        apply_url="https://example.com/jobs/python-engineer",
        location_text="Remote, Brazil",
        country_code="BR",
        workplace_type=WorkplaceType.REMOTE,
        employment_type="full-time",
        published_at=NOW - timedelta(days=2),
    ),
    JobDraft(
        source_key="demo",
        source_name="Demo source",
        source_base_url="https://example.com/jobs",
        source_adapter="demo",
        external_id="demo-csharp-1",
        title="Desenvolvedor C# Pleno",
        company_name="Aurora Digital",
        description="Manutenção de serviços .NET, Azure e SQL Server em São Paulo.",
        canonical_url="https://example.com/jobs/csharp-pleno",
        apply_url="https://example.com/jobs/csharp-pleno",
        location_text="São Paulo, Brasil",
        country_code="BR",
        workplace_type=WorkplaceType.HYBRID,
        employment_type="full-time",
        published_at=NOW - timedelta(days=5),
    ),
    JobDraft(
        source_key="demo",
        source_name="Demo source",
        source_base_url="https://example.com/jobs",
        source_adapter="demo",
        external_id="demo-devops-1",
        title="Staff DevOps Engineer",
        company_name="Orbit Cloud",
        description="Own AWS, Kubernetes and Terraform for a global platform. SRE practices.",
        canonical_url="https://example.com/jobs/devops",
        apply_url="https://example.com/jobs/devops",
        location_text="Remote, United States",
        country_code="US",
        workplace_type=WorkplaceType.REMOTE,
        employment_type="full-time",
        published_at=NOW - timedelta(days=1),
    ),
    JobDraft(
        source_key="demo",
        source_name="Demo source",
        source_base_url="https://example.com/jobs",
        source_adapter="demo",
        external_id="demo-react-1",
        title="Frontend Engineer",
        company_name="Lumen Studio",
        description="React, TypeScript and accessibility-first product work. Hybrid Lisbon.",
        canonical_url="https://example.com/jobs/frontend",
        apply_url="https://example.com/jobs/frontend",
        location_text="Lisbon, Portugal",
        country_code="PT",
        workplace_type=WorkplaceType.HYBRID,
        employment_type="full-time",
        published_at=NOW - timedelta(days=8),
    ),
    JobDraft(
        source_key="demo",
        source_name="Demo source",
        source_base_url="https://example.com/jobs",
        source_adapter="demo",
        external_id="demo-data-1",
        title="Data Engineer",
        company_name="Harbor Analytics",
        description="Airflow, dbt, Spark and Python pipelines for product analytics.",
        canonical_url="https://example.com/jobs/data-engineer",
        apply_url="https://example.com/jobs/data-engineer",
        location_text="Berlin, Germany",
        country_code="DE",
        workplace_type=WorkplaceType.ONSITE,
        employment_type="full-time",
        published_at=NOW - timedelta(days=3),
    ),
]


def main() -> None:
    service = IngestJobService(SQLAlchemyUnitOfWork(), RuleBasedTechnologyClassifier())
    for draft in JOBS:
        service.ingest(draft)
        print(f"seeded {draft.title}")


if __name__ == "__main__":
    main()
