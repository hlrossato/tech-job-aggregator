from typing import TypedDict


class JobItem(TypedDict, total=False):
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
    location_text: str | None
    country_code: str | None
    remote_scope: str | None
    workplace_type: str
    employment_type: str | None
    seniority: str | None
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    language: str | None
    published_at: str | None
    expires_at: str | None
