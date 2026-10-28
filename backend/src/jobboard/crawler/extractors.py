import json
from collections.abc import Iterable
from datetime import UTC, datetime
from html import escape
from typing import Any
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from jobboard.application.html_content import html_to_text, sanitize_html


def _description(value: str | None) -> tuple[str, str | None]:
    return html_to_text(value), sanitize_html(value)


def _listing_payload(html: str) -> dict[str, Any] | None:
    soup = BeautifulSoup(html, "html.parser")
    node = soup.find("script", id="__NEXT_DATA__")
    raw = node.string if node is not None else None
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    listing = payload.get("props", {}).get("pageProps", {}).get("listing")
    return listing if isinstance(listing, dict) else None


def _posting_sections(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    parts: list[str] = []
    for block in soup.select(".careers-listing-details__body"):
        title = block.select_one(".careers-listing-details__body-title")
        content = block.select_one(".careers-listing-details__body-content")
        if title is None or content is None:
            continue
        heading = title.get_text(" ", strip=True)
        inner = content.decode_contents().strip()
        if not heading or not inner:
            continue
        parts.append(f"<h2>{escape(heading)}</h2>{inner}")
    return "".join(parts) or None


def apply_posting_page(item: dict[str, Any], html: str) -> dict[str, Any]:
    """Fill description sections and sidebar facts from the public posting page."""
    updated = dict(item)
    sections = _posting_sections(html)
    if sections:
        description, description_html = _description(sections)
        if description:
            updated["description"] = description
            updated["description_html"] = description_html
    listing = _listing_payload(html)
    if listing is None:
        return updated
    teams = [
        team.get("name")
        for team in listing.get("teams") or []
        if isinstance(team, dict) and team.get("name")
    ]
    offices: list[str] = []
    remotes: list[str] = []
    country_code: str | None = None
    for location in listing.get("locations") or []:
        if not isinstance(location, dict) or not location.get("name"):
            continue
        name = str(location["name"])
        if location.get("remote"):
            remotes.append(name)
        else:
            offices.append(name)
        if country_code is None and location.get("countryCode"):
            country_code = str(location["countryCode"])
    if teams:
        updated["team"] = ", ".join(str(name) for name in teams)
    if offices:
        updated["office_locations"] = ", ".join(offices)
    if remotes:
        updated["remote_location"] = ", ".join(remotes)
    if offices and remotes:
        updated["workplace_type"] = "hybrid"
    elif remotes:
        updated["workplace_type"] = "remote"
    elif offices:
        updated["workplace_type"] = "onsite"
    employment = listing.get("employmentType")
    if employment:
        updated["employment_type"] = str(employment)
    if country_code and not updated.get("country_code"):
        updated["country_code"] = country_code
    for field, key in (
        ("salary_min", "salaryMin"),
        ("salary_max", "salaryMax"),
    ):
        value = listing.get(key)
        if isinstance(value, int):
            updated[field] = value
    currency = listing.get("salaryCurrency")
    if isinstance(currency, str) and currency:
        updated["salary_currency"] = currency
    return updated


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
        description, description_html = _description(job.get("content"))
        items.append(
            {
                "source_key": f"greenhouse-{board}",
                "source_name": f"{company} Greenhouse",
                "source_base_url": source_url,
                "source_adapter": "greenhouse",
                "external_id": str(job["id"]),
                "title": job["title"],
                "company_name": company,
                "description": description,
                "description_html": description_html,
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
        additional_text, additional_html = _description(job.get("additional"))
        description = " ".join(filter(None, (job.get("descriptionPlain"), additional_text)))
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
                "description_html": additional_html,
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
        description, description_html = _description(
            job.get("descriptionHtml") or job.get("descriptionPlain")
        )
        items.append(
            {
                "source_key": f"ashby-{board}",
                "source_name": f"{company} Ashby",
                "source_base_url": source_url,
                "source_adapter": "ashby",
                "external_id": job.get("id") or job.get("jobUrl"),
                "title": job["title"],
                "company_name": company,
                "description": description,
                "description_html": description_html,
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
        description, description_html = _description(job.get("description"))
        items.append(
            {
                "source_key": source_key,
                "source_name": urlsplit(page_url).netloc,
                "source_base_url": page_url,
                "source_adapter": "schema_org",
                "external_id": _identifier(job.get("identifier")),
                "title": job["title"],
                "company_name": company or organization.get("name") or "Unknown company",
                "description": description,
                "description_html": description_html,
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
