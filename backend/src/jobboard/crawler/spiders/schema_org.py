import json
from collections.abc import Iterable
from typing import Any
from urllib.parse import urlsplit

import scrapy
from bs4 import BeautifulSoup


def iter_job_postings(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, list):
        for item in value:
            yield from iter_job_postings(item)
    elif isinstance(value, dict):
        if value.get("@type") == "JobPosting":
            yield value
        for key in ("@graph", "itemListElement"):
            if key in value:
                yield from iter_job_postings(value[key])


class SchemaOrgSpider(scrapy.Spider):
    name = "schema_org"

    def __init__(
        self,
        url: str,
        source_key: str | None = None,
        company: str | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        host = urlsplit(url).netloc.removeprefix("www.")
        self.source_key = source_key or f"schema-{host.replace('.', '-')}"
        self.company = company

    def parse(self, response):
        scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in scripts:
            try:
                payload = json.loads(script)
            except json.JSONDecodeError:
                self.logger.warning("Invalid JSON-LD on %s", response.url)
                continue
            for job in iter_job_postings(payload):
                organization = job.get("hiringOrganization") or {}
                address = (job.get("jobLocation") or {}).get("address", {})
                if isinstance(address, list):
                    address = address[0] if address else {}
                location = ", ".join(
                    filter(
                        None,
                        (
                            address.get("addressLocality"),
                            address.get("addressRegion"),
                            address.get("addressCountry"),
                        ),
                    )
                )
                canonical_url = job.get("url") or response.url
                yield {
                    "source_key": self.source_key,
                    "source_name": urlsplit(response.url).netloc,
                    "source_base_url": response.url,
                    "source_adapter": "schema_org",
                    "external_id": job.get("identifier", {}).get("value")
                    if isinstance(job.get("identifier"), dict)
                    else job.get("identifier"),
                    "title": job["title"],
                    "company_name": self.company or organization.get("name", "Unknown company"),
                    "description": BeautifulSoup(job.get("description", ""), "html.parser").get_text(" "),
                    "canonical_url": canonical_url,
                    "apply_url": canonical_url,
                    "location_text": location or None,
                    "country_code": address.get("addressCountry"),
                    "workplace_type": "remote"
                    if job.get("jobLocationType") == "TELECOMMUTE"
                    else "unspecified",
                    "employment_type": job.get("employmentType"),
                    "published_at": job.get("datePosted"),
                    "expires_at": job.get("validThrough"),
                }
