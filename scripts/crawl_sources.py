#!/usr/bin/env python3
import subprocess
import sys
import tomllib
from pathlib import Path


def main() -> int:
    config_path = Path(sys.argv[1] if len(sys.argv) > 1 else "backend/sources.toml")
    with config_path.open("rb") as config_file:
        sources = tomllib.load(config_file).get("sources", [])

    failed = 0
    for source in sources:
        if not source.get("enabled", False):
            continue
        adapter = source["adapter"]
        command = ["uv", "run", "scrapy", "crawl", adapter]
        for argument in ("board", "site", "url", "company", "source_key"):
            if value := source.get(argument):
                command.extend(["-a", f"{argument}={value}"])
        result = subprocess.run(command, cwd="backend", check=False)
        failed += result.returncode != 0
    return int(failed > 0)


if __name__ == "__main__":
    raise SystemExit(main())
