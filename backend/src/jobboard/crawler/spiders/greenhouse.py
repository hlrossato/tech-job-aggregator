from typing import Any

import scrapy

from jobboard.crawler.extractors import parse_greenhouse_jobs


class GreenhouseSpider(scrapy.Spider):
    name = "greenhouse"
    allowed_domains = ["boards-api.greenhouse.io"]

    def __init__(
        self,
        board: str,
        company: str | None = None,
        source_key: str | None = None,
        grace_minutes: str = "1440",
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.board = board
        self.company = company or board.replace("-", " ").title()
        self.source_url = f"https://boards.greenhouse.io/{board}"
        self.source_key = source_key or f"greenhouse-{board}"
        self.source_name = f"{self.company} Greenhouse"
        self.grace_minutes = int(grace_minutes)

    def start_requests(self) -> Any:
        yield scrapy.Request(
            f"https://boards-api.greenhouse.io/v1/boards/{self.board}/jobs?content=true"
        )

    def parse(self, response: Any) -> Any:
        yield from parse_greenhouse_jobs(
            response.json(),
            board=self.board,
            company=self.company,
            source_url=self.source_url,
        )
