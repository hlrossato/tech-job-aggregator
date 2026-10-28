from typing import Any
from urllib.parse import urlsplit

import scrapy

from jobboard.crawler.extractors import apply_posting_page, parse_greenhouse_jobs


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

    async def start(self) -> Any:
        for request in self.start_requests():
            yield request

    def parse(self, response: Any) -> Any:
        jobs = parse_greenhouse_jobs(
            response.json(),
            board=self.board,
            company=self.company,
            source_url=self.source_url,
        )
        limit = self.settings.getint("CLOSESPIDER_ITEMCOUNT", 0)
        if limit > 0:
            jobs = jobs[:limit]
        for job in jobs:
            url = str(job.get("canonical_url") or "")
            host = urlsplit(url).netloc.removeprefix("www.")
            if host == "stripe.com":
                yield scrapy.Request(
                    url,
                    callback=self.parse_posting,
                    errback=self.keep_job,
                    cb_kwargs={"job": job},
                    meta={"allow_offsite": True},
                )
            else:
                yield job

    def parse_posting(self, response: Any, job: dict[str, Any]) -> dict[str, Any]:
        return apply_posting_page(job, response.text)

    def keep_job(self, failure: Any) -> dict[str, Any] | None:
        job = failure.request.cb_kwargs.get("job")
        return dict(job) if isinstance(job, dict) else None
