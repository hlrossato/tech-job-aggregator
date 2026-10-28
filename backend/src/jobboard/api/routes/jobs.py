from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from jobboard.api.dependencies import SearchServiceDependency
from jobboard.api.schemas import FacetsResponse, JobListResponse, JobResponse
from jobboard.domain.models import JobSearchCriteria, WorkplaceType

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
def search_jobs(
    service: SearchServiceDependency,
    query: Annotated[str | None, Query(alias="q", min_length=1, max_length=200)] = None,
    technologies: Annotated[list[str] | None, Query()] = None,
    role_category: str | None = None,
    country: Annotated[str | None, Query(min_length=2, max_length=2)] = None,
    workplace_type: WorkplaceType | None = None,
    seniority: str | None = None,
    employment_type: str | None = None,
    posted_after: datetime | None = None,
    salary_min: Annotated[int | None, Query(ge=0)] = None,
    sort: Literal["relevance", "newest"] = "relevance",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> JobListResponse:
    criteria = JobSearchCriteria(
        query=query,
        technologies=tuple(technologies or ()),
        role_category=role_category,
        country_code=country,
        workplace_type=workplace_type,
        seniority=seniority,
        employment_type=employment_type,
        posted_after=posted_after,
        salary_min=salary_min,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    return JobListResponse.from_domain(service.search(criteria))


@router.get("/facets", response_model=FacetsResponse)
def list_facets(service: SearchServiceDependency) -> FacetsResponse:
    return FacetsResponse.model_validate(service.facets(), from_attributes=True)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, service: SearchServiceDependency) -> JobResponse:
    job = service.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobResponse.from_domain(job)
