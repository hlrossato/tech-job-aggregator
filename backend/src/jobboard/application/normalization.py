import hashlib
import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAMETERS = {"gclid", "fbclid", "ref", "referrer", "source", "utm_campaign", "utm_content", "utm_medium", "utm_source", "utm_term"}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", " ", normalized).strip()


def normalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    query = urlencode(
        sorted((key, val) for key, val in parse_qsl(parts.query) if key.lower() not in TRACKING_PARAMETERS)
    )
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, ""))


def make_fingerprint(company: str, title: str, location: str | None) -> str:
    identity = "|".join(
        normalize_text(value).casefold() for value in (company, title, location or "")
    )
    return hashlib.sha256(identity.encode()).hexdigest()
