from typing import Any

import scrapy

from jobboard.crawler.extractors import parse_ashby_jobs


class AshbySpider(scrapy.Spider):
    name = "ashby"
    allowed_domains = ["api.ashbyhq.com"]

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
        self.source_url = f"https://jobs.ashbyhq.com/{board}"
        self.source_key = source_key or f"ashby-{board}"
        self.source_name = f"{self.company} Ashby"
        self.grace_minutes = int(grace_minutes)

    def start_requests(self) -> Any:
        yield scrapy.Request(f"https://api.ashbyhq.com/posting-api/job-board/{self.board}")

    async def start(self) -> Any:
        for request in self.start_requests():
            yield request

    def parse(self, response: Any) -> Any:
        yield from parse_ashby_jobs(
            response.json(),
            board=self.board,
            company=self.company,
            source_url=self.source_url,
        )
