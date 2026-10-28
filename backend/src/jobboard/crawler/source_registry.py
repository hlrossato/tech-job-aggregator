import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceConfig:
    key: str
    adapter: str
    enabled: bool
    name: str | None = None
    board: str | None = None
    site: str | None = None
    url: str | None = None
    company: str | None = None
    locale: str | None = None
    frequency_minutes: int = 1440
    grace_minutes: int = 1440
    rate_limit_per_second: float = 1.0
    compliance_notes: str | None = None

    def spider_args(self) -> dict[str, str]:
        args: dict[str, str] = {"source_key": self.key, "grace_minutes": str(self.grace_minutes)}
        if self.board:
            args["board"] = self.board
        if self.site:
            args["site"] = self.site
        if self.url:
            args["url"] = self.url
        if self.company:
            args["company"] = self.company
        return args


def load_sources(path: Path) -> list[SourceConfig]:
    with path.open("rb") as handle:
        payload: dict[str, Any] = tomllib.load(handle)
    sources: list[SourceConfig] = []
    for raw in payload.get("sources", []):
        sources.append(
            SourceConfig(
                key=raw["key"],
                adapter=raw["adapter"],
                enabled=bool(raw.get("enabled", False)),
                name=raw.get("name"),
                board=raw.get("board"),
                site=raw.get("site"),
                url=raw.get("url"),
                company=raw.get("company"),
                locale=raw.get("locale"),
                frequency_minutes=int(raw.get("frequency_minutes", 1440)),
                grace_minutes=int(raw.get("grace_minutes", 1440)),
                rate_limit_per_second=float(raw.get("rate_limit_per_second", 1.0)),
                compliance_notes=raw.get("compliance_notes"),
            )
        )
    return sources
