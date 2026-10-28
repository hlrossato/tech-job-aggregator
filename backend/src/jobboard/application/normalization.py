import hashlib
import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAMETERS = {
    "gclid",
    "fbclid",
    "ref",
    "referrer",
    "source",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", " ", normalized).strip()


def normalize_multiline(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in normalized.split("\n")]
    collapsed: list[str] = []
    previous_blank = False
    for line in lines:
        if not line:
            if collapsed and not previous_blank:
                collapsed.append("")
            previous_blank = True
            continue
        collapsed.append(line)
        previous_blank = False
    return "\n".join(collapsed).strip()


def normalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    query = urlencode(
        sorted(
            (key, val)
            for key, val in parse_qsl(parts.query)
            if key.lower() not in TRACKING_PARAMETERS
        )
    )
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, ""))


COUNTRY_ALIASES = {
    "br": "BR",
    "bra": "BR",
    "brasil": "BR",
    "brazil": "BR",
    "us": "US",
    "usa": "US",
    "united states": "US",
    "united states of america": "US",
    "uk": "GB",
    "gb": "GB",
    "united kingdom": "GB",
    "de": "DE",
    "germany": "DE",
    "pt": "PT",
    "portugal": "PT",
    "ca": "CA",
    "canada": "CA",
    "nl": "NL",
    "netherlands": "NL",
    "ie": "IE",
    "ireland": "IE",
    "es": "ES",
    "spain": "ES",
    "fr": "FR",
    "france": "FR",
    "in": "IN",
    "india": "IN",
    "au": "AU",
    "australia": "AU",
    "remote": None,
}


def make_fingerprint(company: str, title: str, location: str | None) -> str:
    identity = "|".join(
        normalize_text(value).casefold() for value in (company, title, location or "")
    )
    return hashlib.sha256(identity.encode()).hexdigest()


def normalize_country_code(value: str | None, location_text: str | None = None) -> str | None:
    candidates = [value or "", location_text or ""]
    for candidate in candidates:
        folded = normalize_text(candidate).casefold()
        if folded in COUNTRY_ALIASES:
            return COUNTRY_ALIASES[folded]
        if len(folded) == 2 and folded.isalpha():
            return folded.upper()
        for alias, code in COUNTRY_ALIASES.items():
            if alias and alias in folded.split(","):
                return code
            if alias and re.search(rf"\b{re.escape(alias)}\b", folded):
                return code
    return None


def normalize_workplace(value: str | None, location_text: str | None = None) -> str:
    explicit = (value or "").casefold()
    if "hybrid" in explicit or "híbrido" in explicit or "hibrido" in explicit:
        return "hybrid"
    haystack = f"{explicit} {location_text or ''}".casefold()
    if any(token in haystack for token in ("remote", "telecommute", "remoto")):
        return "remote"
    if "hybrid" in haystack or "híbrido" in haystack or "hibrido" in haystack:
        return "hybrid"
    if any(token in haystack for token in ("onsite", "on-site", "office", "presencial")):
        return "onsite"
    return "unspecified"
