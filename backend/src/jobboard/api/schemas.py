from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from jobboard.domain.models import JobView, SearchResult, WorkplaceType


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    company_name: str
    description: str
    canonical_url: HttpUrl
    apply_url: HttpUrl
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
    description_html: str | None = None
    source_name: str | None = None
    source_url: HttpUrl | None = None
    team: str | None = None
    office_locations: str | None = None
    remote_location: str | None = None

    @classmethod
    def from_domain(cls, job: JobView) -> "JobResponse":
        return cls.model_validate(job)


class Pagination(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    pages: int = Field(ge=0)


class JobListResponse(BaseModel):
    items: list[JobResponse]
    pagination: Pagination

    @classmethod
    def from_domain(cls, result: SearchResult) -> "JobListResponse":
        pages = (result.total + result.page_size - 1) // result.page_size
        return cls(
            items=[JobResponse.from_domain(item) for item in result.items],
            pagination=Pagination(
                page=result.page,
                page_size=result.page_size,
                total=result.total,
                pages=pages,
            ),
        )


class FacetsResponse(BaseModel):
    technologies: dict[str, int]
    countries: dict[str, int]
    role_categories: dict[str, int]
    workplace_types: dict[str, int]


class HealthResponse(BaseModel):
    status: str
