from jobboard.application.classification import RuleBasedTechnologyClassifier
from jobboard.application.services import ExpireJobsService, IngestJobService
from jobboard.domain.models import JobDraft, WorkplaceType
from tests.fakes import FakeUnitOfWork


def test_ingest_normalizes_and_classifies() -> None:
    uow = FakeUnitOfWork()
    draft = JobDraft(
        source_key="demo",
        source_name="Demo",
        source_base_url="https://example.com",
        source_adapter="demo",
        external_id="1",
        title="  Senior Python Engineer  ",
        company_name="Acme",
        description="Kubernetes and AWS on a remote team in Brazil.\n\nOwn the platform.",
        description_html="<p>Kubernetes and AWS on a remote team in Brazil.</p>",
        canonical_url="HTTPS://EXAMPLE.COM/jobs/1?utm_source=x",
        apply_url="https://example.com/jobs/1",
        location_text="Remote, Brazil",
        workplace_type=WorkplaceType.UNSPECIFIED,
    )

    IngestJobService(uow, RuleBasedTechnologyClassifier()).ingest(draft)

    stored = uow.jobs.upserted[0]
    assert stored.title == "Senior Python Engineer"
    assert stored.canonical_url == "https://example.com/jobs/1"
    assert stored.country_code == "BR"
    assert stored.workplace_type.value == "remote"
    assert stored.seniority == "senior"
    assert "Python" in stored.technologies
    assert "Own the platform." in stored.description
    assert stored.description_html == "<p>Kubernetes and AWS on a remote team in Brazil.</p>"
    assert uow.committed


def test_expire_unseen_commits() -> None:
    uow = FakeUnitOfWork()
    count = ExpireJobsService(uow).expire_unseen("demo")
    assert count == 1
    assert uow.committed
    assert uow.jobs.expired[0][0] == "demo"
