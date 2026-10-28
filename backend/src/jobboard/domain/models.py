from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class JobStatus(StrEnum):
    ACTIVE = "active"
    STALE = "stale"
    EXPIRED = "expired"


class WorkplaceType(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNSPECIFIED = "unspecified"


@dataclass(slots=True, frozen=True)
class JobDraft:
    source_key: str
    source_name: str
    source_base_url: str
    source_adapter: str
    external_id: str | None
    title: str
    company_name: str
    description: str
    canonical_url: str
    apply_url: str
    location_text: str | None = None
    country_code: str | None = None
    remote_scope: str | None = None
    workplace_type: WorkplaceType = WorkplaceType.UNSPECIFIED
    employment_type: str | None = None
    seniority: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    language: str | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    technologies: tuple[str, ...] = ()
    role_category: str | None = None
    classification_confidence: float | None = None
    classification_reason: str | None = None


@dataclass(slots=True, frozen=True)
class JobSearchCriteria:
    query: str | None = None
    technologies: tuple[str, ...] = ()
    role_category: str | None = None
    country_code: str | None = None
    workplace_type: WorkplaceType | None = None
    seniority: str | None = None
    employment_type: str | None = None
    posted_after: datetime | None = None
    salary_min: int | None = None
    sort: str = "relevance"
    page: int = 1
    page_size: int = 20


@dataclass(slots=True, frozen=True)
class JobView:
    id: UUID
    title: str
    company_name: str
    description: str
    canonical_url: str
    apply_url: str
    location_text: str | None
    country_code: str | None
    workplace_type: WorkplaceType
    employment_type: str | None
    seniority: str | None
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    technologies: tuple[str, ...]
    role_category: str | None
    published_at: datetime | None
    first_seen_at: datetime


@dataclass(slots=True, frozen=True)
class SearchResult:
    items: tuple[JobView, ...]
    total: int
    page: int
    page_size: int


@dataclass(slots=True, frozen=True)
class Facets:
    technologies: dict[str, int] = field(default_factory=dict)
    countries: dict[str, int] = field(default_factory=dict)
    role_categories: dict[str, int] = field(default_factory=dict)
    workplace_types: dict[str, int] = field(default_factory=dict)
