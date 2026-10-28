from datetime import datetime
from uuid import UUID, uuid4

from jobboard.domain.models import Facets, JobDraft, JobSearchCriteria, JobView, SearchResult


class FakeJobRepository:
    def __init__(self, jobs: list[JobView] | None = None):
        self.jobs = list(jobs or [])
        self.upserted: list[JobDraft] = []
        self.expired: list[tuple[str, datetime]] = []
        self.sources: dict[str, tuple[str, str, str]] = {}

    def get(self, job_id: UUID) -> JobView | None:
        return next((job for job in self.jobs if job.id == job_id), None)

    def search(self, criteria: JobSearchCriteria) -> SearchResult:
        items = self.jobs
        if criteria.query:
            needle = criteria.query.casefold()
            items = [
                job
                for job in items
                if needle in job.title.casefold() or needle in job.description.casefold()
            ]
        if criteria.technologies:
            wanted = set(criteria.technologies)
            items = [job for job in items if wanted.intersection(job.technologies)]
        if criteria.country_code:
            items = [job for job in items if job.country_code == criteria.country_code]
        if criteria.workplace_type:
            items = [job for job in items if job.workplace_type == criteria.workplace_type]
        start = (criteria.page - 1) * criteria.page_size
        page = items[start : start + criteria.page_size]
        return SearchResult(
            items=tuple(page), total=len(items), page=criteria.page, page_size=criteria.page_size
        )

    def facets(self) -> Facets:
        technologies: dict[str, int] = {}
        countries: dict[str, int] = {}
        for job in self.jobs:
            for technology in job.technologies:
                technologies[technology] = technologies.get(technology, 0) + 1
            if job.country_code:
                countries[job.country_code] = countries.get(job.country_code, 0) + 1
        return Facets(technologies=technologies, countries=countries)

    def ensure_source(self, key: str, name: str, base_url: str, adapter: str) -> None:
        self.sources[key] = (name, base_url, adapter)

    def upsert(self, draft: JobDraft, fingerprint: str) -> UUID:
        self.upserted.append(draft)
        return uuid4()

    def expire_unseen(self, source_key: str, seen_before: datetime) -> int:
        self.expired.append((source_key, seen_before))
        return 1


class FakeCrawlRunRepository:
    def start(self, source_key: str) -> UUID:
        return uuid4()

    def finish(
        self,
        run_id: UUID,
        *,
        status: str,
        item_count: int,
        error_count: int,
        error_message: str | None = None,
    ) -> None:
        return None


class FakeUnitOfWork:
    def __init__(self, jobs: FakeJobRepository | None = None):
        self.jobs = jobs or FakeJobRepository()
        self.crawl_runs = FakeCrawlRunRepository()
        self.committed = False

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False
