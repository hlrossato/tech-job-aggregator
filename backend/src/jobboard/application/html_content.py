import re
from html import unescape

from bs4 import BeautifulSoup, Tag

ALLOWED_TAGS = {
    "a",
    "b",
    "blockquote",
    "br",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "ul",
}
DISCARDED_TAGS = {"embed", "form", "iframe", "object", "script", "style"}
_HTML_TAG = re.compile(r"</?[a-z][^>]*>", re.IGNORECASE)


def _soup(value: str | None) -> BeautifulSoup:
    return BeautifulSoup(unescape(value or ""), "html.parser")


def looks_like_html(value: str) -> bool:
    return _HTML_TAG.search(value) is not None


def html_to_text(value: str | None) -> str:
    soup = _soup(value)
    for tag in soup.find_all(list(DISCARDED_TAGS)):
        tag.decompose()
    for tag in soup.find_all("br"):
        tag.replace_with("\n")
    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in soup.get_text("\n").split("\n")]
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


def sanitize_html(value: str | None) -> str | None:
    soup = _soup(value)
    if soup.find(True) is None:
        return None
    for tag in soup.find_all(list(DISCARDED_TAGS)):
        tag.decompose()
    for tag in list(soup.find_all(True)):
        if not isinstance(tag, Tag):
            continue
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()
            continue
        if tag.name == "a":
            href = tag.get("href")
            if isinstance(href, str) and href.startswith(("http://", "https://")):
                tag.attrs = {"href": href, "rel": "noreferrer noopener"}
            else:
                tag.unwrap()
            continue
        tag.attrs = {}
    html = soup.decode_contents().strip()
    return html or None


def present_description(description: str, description_html: str | None) -> tuple[str, str | None]:
    if description_html:
        return description, description_html
    if looks_like_html(description):
        return html_to_text(description), sanitize_html(description)
    return description, None
