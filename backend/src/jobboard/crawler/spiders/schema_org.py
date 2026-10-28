import json
from typing import Any
from urllib.parse import urlsplit

import scrapy

from jobboard.crawler.extractors import parse_schema_org_jobs


class SchemaOrgSpider(scrapy.Spider):
    name = "schema_org"

    def __init__(
        self,
        url: str,
        source_key: str | None = None,
        company: str | None = None,
        grace_minutes: str = "1440",
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        host = urlsplit(url).netloc.removeprefix("www.")
        self.source_key = source_key or f"schema-{host.replace('.', '-')}"
        self.company = company
        self.source_url = url
        self.source_name = host
        self.grace_minutes = int(grace_minutes)

    def parse(self, response: Any) -> Any:
        scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in scripts:
            try:
                payload = json.loads(script)
            except json.JSONDecodeError:
                self.logger.warning("Invalid JSON-LD on %s", response.url)
                continue
            yield from parse_schema_org_jobs(
                payload,
                page_url=response.url,
                source_key=self.source_key,
                company=self.company,
            )
