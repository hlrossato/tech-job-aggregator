#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND / "src"))

from jobboard.crawler.source_registry import load_sources  # noqa: E402


def acquire_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("w")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise SystemExit("A crawl is already running")
    return handle


def main() -> int:
    config_path = Path(sys.argv[1] if len(sys.argv) > 1 else BACKEND / "sources.toml")
    lock = acquire_lock(BACKEND / ".crawl-lock")
    failed = 0
    try:
        for source in load_sources(config_path):
            if not source.enabled:
                continue
            command = ["uv", "run", "scrapy", "crawl", source.adapter]
            for key, value in source.spider_args().items():
                command.extend(["-a", f"{key}={value}"])
            print(" ".join(command), flush=True)
            result = subprocess.run(command, cwd=BACKEND, check=False)
            failed += int(result.returncode != 0)
    finally:
        lock.close()
    return int(failed > 0)


if __name__ == "__main__":
    raise SystemExit(main())
