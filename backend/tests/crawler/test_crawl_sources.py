import importlib.util
from pathlib import Path

import pytest

from jobboard.crawler.source_registry import SourceConfig

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "crawl_sources.py"


def load_crawl_sources():
    spec = importlib.util.spec_from_file_location("crawl_sources", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


crawl_sources = load_crawl_sources()


def stripe_source() -> SourceConfig:
    return SourceConfig(
        key="greenhouse-stripe",
        adapter="greenhouse",
        enabled=True,
        board="stripe",
        company="Stripe",
        grace_minutes=2880,
    )


def test_env_limit_is_passed_to_scrapy() -> None:
    limit = crawl_sources.resolve_item_limit(None, {"CRAWL_ITEM_LIMIT": "20"})
    command = crawl_sources.scrapy_command(
        stripe_source(), scrapy_bin="/usr/bin/scrapy", item_limit=limit
    )
    assert command[-2:] == ["-s", "CLOSESPIDER_ITEMCOUNT=20"]
    assert "source_key=greenhouse-stripe" in command


def test_cli_limit_overrides_env() -> None:
    limit = crawl_sources.resolve_item_limit(5, {"CRAWL_ITEM_LIMIT": "20"})
    assert limit == 5


def test_missing_limit_leaves_crawl_uncapped() -> None:
    assert crawl_sources.resolve_item_limit(None, {}) is None
    command = crawl_sources.scrapy_command(stripe_source(), scrapy_bin=None, item_limit=None)
    assert "CLOSESPIDER_ITEMCOUNT" not in " ".join(command)
    assert command[:4] == ["uv", "run", "scrapy", "crawl"]


@pytest.mark.parametrize("raw", ["0", "-3", "many"])
def test_invalid_limit_is_rejected(raw: str) -> None:
    with pytest.raises(SystemExit):
        if raw == "many":
            crawl_sources.resolve_item_limit(None, {"CRAWL_ITEM_LIMIT": raw})
        else:
            crawl_sources.resolve_item_limit(int(raw), {})
