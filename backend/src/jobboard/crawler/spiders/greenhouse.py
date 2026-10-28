from typing import Any

import scrapy
from bs4 import BeautifulSoup


class GreenhouseSpider(scrapy.Spider):
    name = "greenhouse"
    allowed_domains = ["boards-api.greenhouse.io"]

    def __init__(self, board: str, company: str | None = None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.board = board
        self.company = company or board.replace("-", " ").title()
        self.source_url = f"https://boards.greenhouse.io/{board}"

    def start_requests(self):
        yield scrapy.Request(
            f"https://boards-api.greenhouse.io/v1/boards/{self.board}/jobs?content=true"
        )

    def parse(self, response):
        for job in response.json().get("jobs", []):
            location = job.get("location", {}).get("name")
            yield {
                "source_key": f"greenhouse-{self.board}",
                "source_name": f"{self.company} Greenhouse",
                "source_base_url": self.source_url,
                "source_adapter": "greenhouse",
                "external_id": str(job["id"]),
                "title": job["title"],
                "company_name": self.company,
                "description": BeautifulSoup(job.get("content", ""), "html.parser").get_text(" "),
                "canonical_url": job["absolute_url"],
                "apply_url": job["absolute_url"],
                "location_text": location,
                "workplace_type": "remote"
                if location and "remote" in location.casefold()
                else "unspecified",
                "published_at": job.get("updated_at"),
            }
