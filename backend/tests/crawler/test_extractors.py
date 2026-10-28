import json
from pathlib import Path

from jobboard.crawler.extractors import (
    parse_ashby_jobs,
    parse_greenhouse_jobs,
    parse_lever_jobs,
    parse_schema_org_jobs,
)
from jobboard.crawler.source_registry import load_sources

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_greenhouse_fixture() -> None:
    payload = json.loads((FIXTURES / "greenhouse.json").read_text())
    jobs = parse_greenhouse_jobs(
        payload, board="acme", company="Acme", source_url="https://boards.greenhouse.io/acme"
    )
    assert jobs[0]["external_id"] == "42"
    assert jobs[0]["workplace_type"] == "remote"
    assert "Python" in jobs[0]["description"]


def test_parse_lever_and_ashby_fixtures() -> None:
    lever = parse_lever_jobs(
        json.loads((FIXTURES / "lever.json").read_text()),
        site="acme",
        company="Acme",
        source_url="https://jobs.lever.co/acme",
    )
    ashby = parse_ashby_jobs(
        json.loads((FIXTURES / "ashby.json").read_text()),
        board="acme",
        company="Acme",
        source_url="https://jobs.ashbyhq.com/acme",
    )
    assert lever[0]["title"] == "Site Reliability Engineer"
    assert ashby[0]["title"] == "Data Engineer"
    assert ashby[0]["workplace_type"] == "remote"


def test_parse_schema_org_json_ld() -> None:
    html = (FIXTURES / "schema_org.html").read_text()
    start = html.index("{")
    end = html.rindex("}") + 1
    payload = json.loads(html[start:end])
    jobs = parse_schema_org_jobs(
        payload,
        page_url="https://careers.example.com",
        source_key="schema-example",
        company=None,
    )
    assert jobs[0]["title"] == "Security Engineer"
    assert jobs[0]["country_code"] == "BR"


def test_source_registry_loads_example(tmp_path: Path) -> None:
    config = tmp_path / "sources.toml"
    config.write_text(
        """
[[sources]]
key = "stripe"
adapter = "greenhouse"
board = "stripe"
company = "Stripe"
enabled = false
"""
    )
    sources = load_sources(config)
    assert sources[0].key == "stripe"
    assert sources[0].spider_args()["board"] == "stripe"
    assert sources[0].enabled is False
