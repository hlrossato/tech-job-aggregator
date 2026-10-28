from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

from bs4 import BeautifulSoup


def html_to_text(value: str | None) -> str:
    return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)


def _identifier(value: Any) -> str | None:
    if isinstance(value, dict):
        raw = value.get("value") or value.get("name")
        return str(raw) if raw is not None else None
    if value is None:
        return None
    return str(value)


def parse_greenhouse_jobs(
    payload: dict[str, Any], *, board: str, company: str, source_url: str
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for job in payload.get("jobs", []):
        location = (job.get("location") or {}).get("name")
        items.append(
            {
                "source_key": f"greenhouse-{board}",
                "source_name": f"{company} Greenhouse",
                "source_base_url": source_url,
                "source_adapter": "greenhouse",
                "external_id": str(job["id"]),
                "title": job["title"],
                "company_name": company,
                "description": html_to_text(job.get("content")),
                "canonical_url": job["absolute_url"],
                "apply_url": job["absolute_url"],
                "location_text": location,
                "workplace_type": "remote"
                if location and "remote" in location.casefold()
                else "unspecified",
                "published_at": job.get("updated_at"),
            }
        )
    return items


def parse_lever_jobs(
    payload: list[dict[str, Any]], *, site: str, company: str, source_url: str
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for job in payload:
        categories = job.get("categories") or {}
        location = categories.get("location")
        created_at = job.get("createdAt")
        published = (
            datetime.fromtimestamp(created_at / 1000, UTC).isoformat() if created_at else None
        )
        description = " ".join(
            filter(
                None,
                (job.get("descriptionPlain"), html_to_text(job.get("additional"))),
            )
        )
        items.append(
            {
                "source_key": f"lever-{site}",
                "source_name": f"{company} Lever",
                "source_base_url": source_url,
                "source_adapter": "lever",
                "external_id": job["id"],
                "title": job["text"],
                "company_name": company,
                "description": description,
                "canonical_url": job["hostedUrl"],
                "apply_url": job.get("applyUrl", job["hostedUrl"]),
                "location_text": location,
                "workplace_type": job.get("workplaceType", "unspecified"),
                "employment_type": categories.get("commitment"),
                "published_at": published,
            }
        )
    return items


def parse_ashby_jobs(
    payload: dict[str, Any], *, board: str, company: str, source_url: str
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for job in payload.get("jobs", []):
        location = job.get("location")
        items.append(
            {
                "source_key": f"ashby-{board}",
                "source_name": f"{company} Ashby",
                "source_base_url": source_url,
                "source_adapter": "ashby",
                "external_id": job.get("id") or job.get("jobUrl"),
                "title": job["title"],
                "company_name": company,
                "description": html_to_text(
                    job.get("descriptionHtml") or job.get("descriptionPlain")
                ),
                "canonical_url": job["jobUrl"],
                "apply_url": job.get("applyUrl", job["jobUrl"]),
                "location_text": location,
                "workplace_type": "remote" if job.get("isRemote") else "unspecified",
                "employment_type": job.get("employmentType"),
                "published_at": job.get("publishedAt"),
            }
        )
    return items


def iter_job_postings(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, list):
        for item in value:
            yield from iter_job_postings(item)
    elif isinstance(value, dict):
        types = value.get("@type")
        if types == "JobPosting" or (isinstance(types, list) and "JobPosting" in types):
            yield value
        for key in ("@graph", "itemListElement"):
            if key in value:
                yield from iter_job_postings(value[key])


def parse_schema_org_jobs(
    payload: Any,
    *,
    page_url: str,
    source_key: str,
    company: str | None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for job in iter_job_postings(payload):
        organization = job.get("hiringOrganization") or {}
        location = job.get("jobLocation") or {}
        if isinstance(location, list):
            location = location[0] if location else {}
        address = location.get("address", {}) if isinstance(location, dict) else {}
        if isinstance(address, list):
            address = address[0] if address else {}
        location_text = ", ".join(
            filter(
                None,
                (
                    address.get("addressLocality"),
                    address.get("addressRegion"),
                    address.get("addressCountry"),
                ),
            )
        )
        canonical_url = job.get("url") or page_url
        country = address.get("addressCountry")
        items.append(
            {
                "source_key": source_key,
                "source_name": urlsplit(page_url).netloc,
                "source_base_url": page_url,
                "source_adapter": "schema_org",
                "external_id": _identifier(job.get("identifier")),
                "title": job["title"],
                "company_name": company or organization.get("name") or "Unknown company",
                "description": html_to_text(job.get("description")),
                "canonical_url": canonical_url,
                "apply_url": canonical_url,
                "location_text": location_text or None,
                "country_code": country if isinstance(country, str) else None,
                "workplace_type": "remote"
                if job.get("jobLocationType") == "TELECOMMUTE"
                else "unspecified",
                "employment_type": job.get("employmentType"),
                "published_at": job.get("datePosted"),
                "expires_at": job.get("validThrough"),
            }
        )
    return items
