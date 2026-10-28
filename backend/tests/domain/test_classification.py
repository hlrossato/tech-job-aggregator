from jobboard.application.classification import RuleBasedTechnologyClassifier, detect_seniority
from jobboard.application.normalization import (
    make_fingerprint,
    normalize_country_code,
    normalize_url,
    normalize_workplace,
)


def test_classifies_technology_and_role_from_title_and_description() -> None:
    technologies, role, confidence = RuleBasedTechnologyClassifier().classify(
        "Senior DevOps Engineer",
        "Build our AWS platform with Kubernetes and Terraform.",
    )

    assert role == "devops-sre"
    assert {"AWS", "Kubernetes", "Terraform"} <= set(technologies)
    assert confidence > 0.5


def test_normalize_url_removes_tracking_and_preserves_business_parameters() -> None:
    url = normalize_url("HTTPS://EXAMPLE.COM/jobs/1/?utm_source=x&department=eng")

    assert url == "https://example.com/jobs/1?department=eng"


def test_fingerprint_is_case_and_whitespace_insensitive() -> None:
    first = make_fingerprint("Acme", "Python  Developer", "Brazil")
    second = make_fingerprint("ACME", "Python Developer", "brazil")

    assert first == second


def test_country_workplace_and_seniority_helpers() -> None:
    assert normalize_country_code(None, "Remote, Brazil") == "BR"
    assert normalize_workplace("unspecified", "Remote-friendly") == "remote"
    assert detect_seniority("Desenvolvedor C# Pleno") == "mid"
