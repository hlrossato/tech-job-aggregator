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
    assert "<" not in jobs[0]["description"]
    assert jobs[0]["description_html"] == "<p>Python and Django</p>"


def test_posting_page_includes_sidebar_and_extra_sections() -> None:
    from jobboard.crawler.extractors import apply_posting_page

    html = """
    <script id="__NEXT_DATA__" type="application/json">
    {"props":{"pageProps":{"listing":{
      "employmentType":"Full time",
      "salaryMin":144300,
      "salaryMax":216500,
      "salaryCurrency":"USD",
      "teams":[{"name":"Security"}],
      "locations":[
        {"name":"Remote in United States","remote":true,"countryCode":"US"},
        {"name":"Atlanta","remote":false,"countryCode":"US"},
        {"name":"South San Francisco HQ","remote":false,"countryCode":"US"}
      ]
    }}}}
    </script>
    <div class="careers-listing-details__body">
      <h2 class="careers-listing-details__body-title">Who we are</h2>
      <div class="careers-listing-details__body-content"><p>About Stripe.</p></div>
    </div>
    <div class="careers-listing-details__body">
      <h2 class="careers-listing-details__body-title">Hybrid work at Stripe</h2>
      <div class="careers-listing-details__body-content"><p>Office or remote.</p></div>
    </div>
    <div class="careers-listing-details__body">
      <h2 class="careers-listing-details__body-title">Pay and benefits</h2>
      <div class="careers-listing-details__body-content">
        <p>The annual US base salary range is stated here.</p>
      </div>
    </div>
    """
    job = apply_posting_page({"description": "partial", "country_code": None}, html)
    assert "Who we are" in job["description"]
    assert "Hybrid work at Stripe" in job["description"]
    assert "Pay and benefits" in job["description"]
    assert "<h2>Hybrid work at Stripe</h2>" in job["description_html"]
    assert job["team"] == "Security"
    assert job["office_locations"] == "Atlanta, South San Francisco HQ"
    assert job["remote_location"] == "Remote in United States"
    assert job["employment_type"] == "Full time"
    assert job["workplace_type"] == "hybrid"
    assert job["salary_min"] == 144300
    assert job["country_code"] == "US"


def test_parse_greenhouse_unescapes_markup() -> None:
    jobs = parse_greenhouse_jobs(
        {
            "jobs": [
                {
                    "id": 7,
                    "title": "Backend Engineer",
                    "absolute_url": "https://boards.greenhouse.io/acme/jobs/7",
                    "location": {"name": "Remote"},
                    "content": (
                        "&lt;h2&gt;Who we are&lt;/h2&gt;"
                        "&lt;ul&gt;&lt;li&gt;Python&lt;/li&gt;&lt;li&gt;PostgreSQL&lt;/li&gt;&lt;/ul&gt;"
                        "&lt;script&gt;alert(1)&lt;/script&gt;"
                    ),
                }
            ]
        },
        board="acme",
        company="Acme",
        source_url="https://boards.greenhouse.io/acme",
    )
    assert jobs[0]["description"] == "Who we are\nPython\nPostgreSQL"
    assert "<script" not in (jobs[0]["description_html"] or "")
    assert "alert" not in (jobs[0]["description_html"] or "")
    assert "<h2>Who we are</h2>" in jobs[0]["description_html"]
    assert "<li>Python</li>" in jobs[0]["description_html"]


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


def test_posting_place_is_the_board() -> None:
    from jobboard.infrastructure.repositories.sqlalchemy import posting_place_label

    assert posting_place_label("greenhouse", "Stripe Greenhouse") == "Greenhouse"
    assert posting_place_label("lever", "Netflix Lever") == "Lever"
    assert posting_place_label("ashby", "Vercel Ashby") == "Ashby"
    assert posting_place_label("demo", "Demo source") == "Demo source"


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
