from collections.abc import Iterable
from datetime import datetime
from typing import Protocol, Self
from uuid import UUID

from jobboard.domain.models import Facets, JobDraft, JobSearchCriteria, JobView, SearchResult


class JobRepository(Protocol):
    def get(self, job_id: UUID) -> JobView | None: ...

    def search(self, criteria: JobSearchCriteria) -> SearchResult: ...

    def facets(self) -> Facets: ...

    def ensure_source(self, key: str, name: str, base_url: str, adapter: str) -> None: ...

    def upsert(self, draft: JobDraft, fingerprint: str) -> UUID: ...

    def expire_unseen(self, source_key: str, seen_before: datetime) -> int: ...


class CrawlRunRepository(Protocol):
    def start(self, source_key: str) -> UUID: ...

    def finish(
        self,
        run_id: UUID,
        *,
        status: str,
        item_count: int,
        error_count: int,
        error_message: str | None = None,
    ) -> None: ...


class UnitOfWork(Protocol):
    jobs: JobRepository
    crawl_runs: CrawlRunRepository

    def __enter__(self) -> Self: ...

    def __exit__(self, *args: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class TechnologyClassifier(Protocol):
    def classify(self, title: str, description: str) -> tuple[Iterable[str], str | None, float]: ...
