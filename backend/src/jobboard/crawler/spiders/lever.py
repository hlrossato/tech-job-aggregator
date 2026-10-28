from datetime import UTC, datetime
from typing import Any

import scrapy
from bs4 import BeautifulSoup


class LeverSpider(scrapy.Spider):
    name = "lever"
    allowed_domains = ["api.lever.co"]

    def __init__(self, site: str, company: str | None = None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.site = site
        self.company = company or site.replace("-", " ").title()
        self.source_url = f"https://jobs.lever.co/{site}"

    def start_requests(self):
        yield scrapy.Request(f"https://api.lever.co/v0/postings/{self.site}?mode=json")

    def parse(self, response):
        for job in response.json():
            categories = job.get("categories", {})
            location = categories.get("location")
            created_at = job.get("createdAt")
            published = (
                datetime.fromtimestamp(created_at / 1000, UTC).isoformat()
                if created_at
                else None
            )
            description = " ".join(
                filter(
                    None,
                    (
                        job.get("descriptionPlain"),
                        BeautifulSoup(job.get("additional", ""), "html.parser").get_text(" "),
                    ),
                )
            )
            yield {
                "source_key": f"lever-{self.site}",
                "source_name": f"{self.company} Lever",
                "source_base_url": self.source_url,
                "source_adapter": "lever",
                "external_id": job["id"],
                "title": job["text"],
                "company_name": self.company,
                "description": description,
                "canonical_url": job["hostedUrl"],
                "apply_url": job.get("applyUrl", job["hostedUrl"]),
                "location_text": location,
                "workplace_type": job.get("workplaceType", "unspecified"),
                "employment_type": categories.get("commitment"),
                "published_at": published,
            }
