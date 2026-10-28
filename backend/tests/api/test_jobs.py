from fastapi.testclient import TestClient

from jobboard.api.dependencies import get_search_service
from jobboard.api.main import app
from jobboard.application.services import SearchJobsService
from tests.conftest import make_job
from tests.fakes import FakeJobRepository


def _client(jobs: list | None = None) -> TestClient:
    service = SearchJobsService(FakeJobRepository(jobs or []))
    app.dependency_overrides[get_search_service] = lambda: service
    return TestClient(app)


def test_health() -> None:
    response = _client().get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_returns_jobs() -> None:
    job = make_job()
    response = _client([job]).get("/api/v1/jobs", params={"q": "python"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["total"] == 1
    assert payload["items"][0]["title"] == job.title
    assert payload["items"][0]["apply_url"].startswith("https://")


def test_get_job_not_found() -> None:
    response = _client().get("/api/v1/jobs/11111111-1111-1111-1111-111111111111")
    assert response.status_code == 404


def test_get_job_and_facets() -> None:
    job = make_job()
    client = _client([job])
    detail = client.get(f"/api/v1/jobs/{job.id}")
    assert detail.status_code == 200
    assert detail.json()["company_name"] == "Northwind Labs"
    assert detail.json()["source_name"] == "Demo source"
    assert detail.json()["source_url"] == "https://example.com/jobs"
    facets = client.get("/api/v1/jobs/facets")
    assert facets.status_code == 200
    assert facets.json()["technologies"]["Python"] == 1
