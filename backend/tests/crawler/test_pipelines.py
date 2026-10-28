import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from scrapy.exceptions import DropItem

from jobboard.crawler.pipelines import DatabasePipeline
from jobboard.crawler.spiders.ashby import AshbySpider
from jobboard.crawler.spiders.greenhouse import GreenhouseSpider
from jobboard.crawler.spiders.lever import LeverSpider
from tests.fakes import FakeUnitOfWork

ITEM = {
    "source_key": "greenhouse-stripe",
    "source_name": "Stripe Greenhouse",
    "source_base_url": "https://boards.greenhouse.io/stripe",
    "source_adapter": "greenhouse",
    "external_id": "1",
    "title": "Software Engineer",
    "company_name": "Stripe",
    "description": "Build payments with Python.",
    "canonical_url": "https://boards.greenhouse.io/stripe/jobs/1",
    "apply_url": "https://boards.greenhouse.io/stripe/jobs/1",
}


class Engine:
    def __init__(self) -> None:
        self.reasons: list[str] = []

    def close_spider(self, spider: object, reason: str) -> None:
        self.reasons.append(reason)


class Settings:
    def __init__(self, limit: int) -> None:
        self.limit = limit

    def getint(self, key: str, default: int = 0) -> int:
        assert key == "CLOSESPIDER_ITEMCOUNT"
        return self.limit


class Stats:
    def get_value(self, key: str, default: int = 0) -> int:
        return default


class Logger:
    def info(self, message: str, *args: object) -> None:
        return None


def spider_stub(limit: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        name="greenhouse",
        source_key="greenhouse-stripe",
        source_name="Stripe Greenhouse",
        source_url="https://boards.greenhouse.io/stripe",
        grace_minutes=2880,
        logger=Logger(),
        crawler=SimpleNamespace(settings=Settings(limit), stats=Stats(), engine=Engine()),
    )


def pipeline_with(uow: FakeUnitOfWork) -> DatabasePipeline:
    pipeline = DatabasePipeline()
    pipeline.uow_factory = lambda: uow  # type: ignore[method-assign, assignment]
    return pipeline


def test_open_spider_reads_item_cap() -> None:
    uow = FakeUnitOfWork()
    pipeline = pipeline_with(uow)
    pipeline.open_spider(spider_stub(20))  # type: ignore[arg-type]
    assert pipeline.item_limit == 20
    assert "greenhouse-stripe" in uow.jobs.sources


def test_pipeline_stops_before_the_next_insert() -> None:
    uow = FakeUnitOfWork()
    pipeline = pipeline_with(uow)
    spider = spider_stub(1)
    pipeline.item_limit = 1

    pipeline.process_item(ITEM, spider)  # type: ignore[arg-type]
    assert pipeline.item_count == 1
    assert len(uow.jobs.upserted) == 1

    with pytest.raises(DropItem, match="item limit 1"):
        pipeline.process_item(ITEM, spider)  # type: ignore[arg-type]
    assert len(uow.jobs.upserted) == 1
    assert spider.crawler.engine.reasons == ["closespider_itemcount"]

    with pytest.raises(DropItem):
        pipeline.process_item(ITEM, spider)  # type: ignore[arg-type]
    assert spider.crawler.engine.reasons == ["closespider_itemcount"]


def test_capped_close_skips_expire() -> None:
    uow = FakeUnitOfWork()
    pipeline = pipeline_with(uow)
    pipeline.run_id = uuid4()
    pipeline.source_key = "greenhouse-stripe"
    pipeline.started_at = datetime(2026, 10, 28, tzinfo=UTC)
    pipeline.item_limit = 20
    pipeline.item_count = 20

    pipeline.close_spider(spider_stub())  # type: ignore[arg-type]

    assert uow.jobs.expired == []
    assert uow.committed is True


def test_spiders_start_fetches_the_board() -> None:
    async def first_url(spider: GreenhouseSpider | LeverSpider | AshbySpider) -> str:
        async for request in spider.start():
            return str(request.url)
        raise AssertionError("spider produced no start request")

    greenhouse = GreenhouseSpider(board="stripe", company="Stripe", source_key="greenhouse-stripe")
    lever = LeverSpider(site="netflix", company="Netflix", source_key="lever-netflix")
    ashby = AshbySpider(board="vercel", company="Vercel", source_key="ashby-vercel")
    assert (
        asyncio.run(first_url(greenhouse))
        == "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
    )
    assert asyncio.run(first_url(lever)) == "https://api.lever.co/v0/postings/netflix?mode=json"
    assert asyncio.run(first_url(ashby)) == "https://api.ashbyhq.com/posting-api/job-board/vercel"


def test_uncapped_close_expires_unseen() -> None:
    uow = FakeUnitOfWork()
    pipeline = pipeline_with(uow)
    pipeline.run_id = uuid4()
    pipeline.source_key = "greenhouse-stripe"
    pipeline.started_at = datetime(2026, 10, 28, tzinfo=UTC)
    pipeline.item_limit = 0

    pipeline.close_spider(spider_stub())  # type: ignore[arg-type]

    assert len(uow.jobs.expired) == 1
    assert uow.jobs.expired[0][0] == "greenhouse-stripe"
