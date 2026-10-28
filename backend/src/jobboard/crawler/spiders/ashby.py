from typing import Any

import scrapy
from bs4 import BeautifulSoup


class AshbySpider(scrapy.Spider):
    name = "ashby"
    allowed_domains = ["api.ashbyhq.com"]

    def __init__(self, board: str, company: str | None = None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.board = board
        self.company = company or board.replace("-", " ").title()
        self.source_url = f"https://jobs.ashbyhq.com/{board}"

    def start_requests(self):
        yield scrapy.Request(f"https://api.ashbyhq.com/posting-api/job-board/{self.board}")

    def parse(self, response):
        for job in response.json().get("jobs", []):
            location = job.get("location")
            is_remote = job.get("isRemote", False)
            yield {
                "source_key": f"ashby-{self.board}",
                "source_name": f"{self.company} Ashby",
                "source_base_url": self.source_url,
                "source_adapter": "ashby",
                "external_id": job.get("id") or job.get("jobUrl"),
                "title": job["title"],
                "company_name": self.company,
                "description": BeautifulSoup(
                    job.get("descriptionHtml", job.get("descriptionPlain", "")), "html.parser"
                ).get_text(" "),
                "canonical_url": job["jobUrl"],
                "apply_url": job.get("applyUrl", job["jobUrl"]),
                "location_text": location,
                "workplace_type": "remote" if is_remote else "unspecified",
                "employment_type": job.get("employmentType"),
                "published_at": job.get("publishedAt"),
            }
