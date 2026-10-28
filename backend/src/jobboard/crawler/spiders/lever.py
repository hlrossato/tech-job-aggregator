from typing import Any

import scrapy

from jobboard.crawler.extractors import parse_lever_jobs


class LeverSpider(scrapy.Spider):
    name = "lever"
    allowed_domains = ["api.lever.co"]

    def __init__(
        self,
        site: str,
        company: str | None = None,
        source_key: str | None = None,
        grace_minutes: str = "1440",
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.site = site
        self.company = company or site.replace("-", " ").title()
        self.source_url = f"https://jobs.lever.co/{site}"
        self.source_key = source_key or f"lever-{site}"
        self.source_name = f"{self.company} Lever"
        self.grace_minutes = int(grace_minutes)

    def start_requests(self) -> Any:
        yield scrapy.Request(f"https://api.lever.co/v0/postings/{self.site}?mode=json")

    def parse(self, response: Any) -> Any:
        yield from parse_lever_jobs(
            response.json(),
            site=self.site,
            company=self.company,
            source_url=self.source_url,
        )
