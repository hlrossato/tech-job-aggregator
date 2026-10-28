from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID

from scrapy import Spider
from scrapy.exceptions import DropItem

from jobboard.application.classification import RuleBasedTechnologyClassifier
from jobboard.application.services import ExpireJobsService, IngestJobService
from jobboard.domain.models import JobDraft, WorkplaceType
from jobboard.infrastructure.repositories.sqlalchemy import SQLAlchemyUnitOfWork

REQUIRED_FIELDS = (
    "source_key",
    "source_name",
    "source_base_url",
    "source_adapter",
    "title",
    "company_name",
    "description",
    "canonical_url",
    "apply_url",
)


class ValidationPipeline:
    def process_item(self, item: dict[str, Any], spider: Spider) -> dict[str, Any]:
        missing = [field for field in REQUIRED_FIELDS if not item.get(field)]
        if missing:
            raise DropItem(f"Missing required fields: {', '.join(missing)}")
        for field in ("canonical_url", "apply_url"):
            if urlsplit(item[field]).scheme not in {"http", "https"}:
                raise DropItem(f"Unsupported {field}")
        return item


def _date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class DatabasePipeline:
    def __init__(self) -> None:
        self.uow_factory = SQLAlchemyUnitOfWork
        self.classifier = RuleBasedTechnologyClassifier()
        self.run_id: UUID | None = None
        self.source_key: str | None = None
        self.started_at: datetime | None = None
        self.item_count = 0
        self.error_count = 0

    def open_spider(self, spider: Spider) -> None:
        source_key = getattr(spider, "source_key", spider.name)
        source_name = getattr(spider, "source_name", spider.name)
        source_url = getattr(spider, "source_url", "")
        self.source_key = source_key
        self.started_at = datetime.now(UTC)
        with self.uow_factory() as uow:
            uow.jobs.ensure_source(source_key, source_name, source_url, spider.name)
            self.run_id = uow.crawl_runs.start(source_key)
            uow.commit()

    def process_item(self, item: dict[str, Any], spider: Spider) -> dict[str, Any]:
        try:
            workplace_type = WorkplaceType(item.get("workplace_type", "unspecified"))
        except ValueError:
            workplace_type = WorkplaceType.UNSPECIFIED
        draft = JobDraft(
            source_key=item["source_key"],
            source_name=item["source_name"],
            source_base_url=item["source_base_url"],
            source_adapter=item["source_adapter"],
            external_id=item.get("external_id"),
            title=item["title"],
            company_name=item["company_name"],
            description=item["description"],
            canonical_url=item["canonical_url"],
            apply_url=item["apply_url"],
            location_text=item.get("location_text"),
            country_code=item.get("country_code"),
            remote_scope=item.get("remote_scope"),
            workplace_type=workplace_type,
            employment_type=item.get("employment_type"),
            seniority=item.get("seniority"),
            salary_min=item.get("salary_min"),
            salary_max=item.get("salary_max"),
            salary_currency=item.get("salary_currency"),
            language=item.get("language"),
            published_at=_date(item.get("published_at")),
            expires_at=_date(item.get("expires_at")),
        )
        IngestJobService(self.uow_factory(), self.classifier).ingest(draft)
        self.item_count += 1
        return item

    def close_spider(self, spider: Spider) -> None:
        if self.run_id is None or self.source_key is None or self.started_at is None:
            return
        errors = int(spider.crawler.stats.get_value("log_count/ERROR", 0))
        self.error_count = errors
        grace_minutes = int(getattr(spider, "grace_minutes", 1440))
        cutoff = self.started_at - timedelta(minutes=grace_minutes)
        expire_service = ExpireJobsService(self.uow_factory())
        expire_service.expire_unseen(self.source_key, cutoff)
        with self.uow_factory() as uow:
            uow.crawl_runs.finish(
                self.run_id,
                status="succeeded" if errors == 0 else "completed_with_errors",
                item_count=self.item_count,
                error_count=errors,
            )
            uow.commit()
