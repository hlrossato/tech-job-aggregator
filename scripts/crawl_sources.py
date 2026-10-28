#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import os
import shutil
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND / "src"))

from jobboard.crawler.source_registry import SourceConfig, load_sources  # noqa: E402


def acquire_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("w")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise SystemExit("A crawl is already running") from None
    return handle


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl enabled job sources")
    parser.add_argument("config", nargs="?", type=Path, default=BACKEND / "sources.toml")
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args(argv)


def resolve_item_limit(
    cli_limit: int | None, environ: Mapping[str, str] | None = None
) -> int | None:
    env = os.environ if environ is None else environ
    limit = cli_limit
    if limit is None:
        raw = env.get("CRAWL_ITEM_LIMIT", "").strip()
        if raw:
            try:
                limit = int(raw)
            except ValueError:
                raise SystemExit("CRAWL_ITEM_LIMIT must be a positive integer") from None
    if limit is None:
        return None
    if limit < 1:
        raise SystemExit("Item limit must be a positive integer")
    return limit


def scrapy_command(
    source: SourceConfig, *, scrapy_bin: str | None, item_limit: int | None
) -> list[str]:
    if scrapy_bin is None:
        command = ["uv", "run", "scrapy", "crawl", source.adapter]
    else:
        command = [scrapy_bin, "crawl", source.adapter]
    for key, value in source.spider_args().items():
        command.extend(["-a", f"{key}={value}"])
    if item_limit is not None:
        command.extend(["-s", f"CLOSESPIDER_ITEMCOUNT={item_limit}"])
    return command


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    item_limit = resolve_item_limit(args.limit)
    lock = acquire_lock(BACKEND / ".crawl-lock")
    failed = 0
    try:
        for source in load_sources(args.config):
            if not source.enabled:
                continue
            command = scrapy_command(
                source, scrapy_bin=shutil.which("scrapy"), item_limit=item_limit
            )
            print(" ".join(command), flush=True)
            result = subprocess.run(command, cwd=BACKEND, check=False)
            failed += int(result.returncode != 0)
    finally:
        lock.close()
    return int(failed > 0)


if __name__ == "__main__":
    raise SystemExit(main())
