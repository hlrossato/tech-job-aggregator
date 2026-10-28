from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

from jobboard.application.classification import detect_seniority
from jobboard.application.normalization import (
    make_fingerprint,
    normalize_country_code,
    normalize_text,
    normalize_url,
    normalize_workplace,
)
from jobboard.domain.models import (
    Facets,
    JobDraft,
    JobSearchCriteria,
    JobView,
    SearchResult,
    WorkplaceType,
)
from jobboard.domain.repositories import JobRepository, TechnologyClassifier, UnitOfWork


class SearchJobsService:
    def __init__(self, jobs: JobRepository):
        self.jobs = jobs

    def search(self, criteria: JobSearchCriteria) -> SearchResult:
        return self.jobs.search(criteria)

    def get(self, job_id: UUID) -> JobView | None:
        return self.jobs.get(job_id)

    def facets(self) -> Facets:
        return self.jobs.facets()


class IngestJobService:
    def __init__(self, uow: UnitOfWork, classifier: TechnologyClassifier):
        self.uow = uow
        self.classifier = classifier

    def ingest(self, draft: JobDraft) -> UUID:
        technologies, role_category, confidence = self.classifier.classify(
            draft.title, draft.description
        )
        normalized = replace(
            draft,
            title=normalize_text(draft.title),
            company_name=normalize_text(draft.company_name),
            description=normalize_text(draft.description),
            canonical_url=normalize_url(draft.canonical_url),
            apply_url=normalize_url(draft.apply_url),
            location_text=normalize_text(draft.location_text) if draft.location_text else None,
            country_code=normalize_country_code(draft.country_code, draft.location_text),
            workplace_type=WorkplaceType(
                normalize_workplace(draft.workplace_type.value, draft.location_text)
            ),
            seniority=draft.seniority or detect_seniority(draft.title),
            technologies=draft.technologies or tuple(technologies),
            role_category=draft.role_category or role_category,
            classification_confidence=draft.classification_confidence or confidence,
            classification_reason=draft.classification_reason or "rule-based taxonomy",
        )
        fingerprint = make_fingerprint(
            normalized.company_name, normalized.title, normalized.location_text
        )
        with self.uow:
            job_id = self.uow.jobs.upsert(normalized, fingerprint)
            self.uow.commit()
            return job_id


class ExpireJobsService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def expire_unseen(self, source_key: str, seen_before: datetime | None = None) -> int:
        cutoff = seen_before or datetime.now(UTC)
        with self.uow:
            count = self.uow.jobs.expire_unseen(source_key, cutoff)
            self.uow.commit()
            return count
