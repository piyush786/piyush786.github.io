from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "portfolio-site"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.local_refs: list[str] = []
        self.fragments: list[str] = []
        self.scripts: list[tuple[dict[str, str], str]] = []
        self.images: list[dict[str, str]] = []
        self._json_attrs: dict[str, str] | None = None
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.add(values["id"])

        if tag in {"a", "link", "script", "img", "source"}:
            for key in ("href", "src", "srcset"):
                if values.get(key):
                    self.local_refs.append(values[key])

        if tag == "a" and values.get("href", "").startswith("#"):
            self.fragments.append(values["href"][1:])

        if tag == "img":
            self.images.append(values)

        if tag == "script" and values.get("type") == "application/ld+json":
            self._json_attrs = values
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._json_attrs is not None:
            self._json_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_attrs is not None:
            self.scripts.append((self._json_attrs, "".join(self._json_parts)))
            self._json_attrs = None
            self._json_parts = []


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> None:
    html_path = SITE / "index.html"
    html = html_path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(html)

    required_ids = {
        "top",
        "projects",
        "about",
        "leadership",
        "experience",
        "stack",
        "credentials",
        "contact",
    }
    require(
        required_ids <= parser.ids,
        f"missing section ids: {sorted(required_ids - parser.ids)}",
    )
    require(
        not (set(parser.fragments) - parser.ids),
        f"broken fragment links: {sorted(set(parser.fragments) - parser.ids)}",
    )

    for phrase in (
        "I lead secure banking platforms",
        "Selected work",
        "Technical Lead in Riyadh",
        "Let's connect",
    ):
        require(
            phrase.lower() in html.lower(),
            f"missing personal portfolio phrase: {phrase}",
        )

    for forbidden in (
        "our services",
        "book a consultation",
        "we build",
        "our clients",
    ):
        require(
            forbidden not in html.lower(),
            f"agency language present: {forbidden}",
        )

    local_refs: set[str] = set()
    for ref in parser.local_refs:
        for candidate in ref.split(","):
            candidate = candidate.strip().split()[0]
            parsed = urlparse(candidate)
            if (
                not candidate
                or parsed.scheme
                or candidate.startswith(("#", "mailto:", "tel:"))
            ):
                continue
            local_refs.add(parsed.path)

    missing = sorted(
        ref for ref in local_refs if ref and not (SITE / ref.lstrip("/")).exists()
    )
    require(not missing, f"missing local assets: {missing}")

    for image in parser.images:
        require(bool(image.get("alt")), f"image missing alt: {image.get('src')}")
        require(
            bool(image.get("width")) and bool(image.get("height")),
            f"image missing dimensions: {image.get('src')}",
        )

    require(parser.scripts, "missing JSON-LD")
    for _, payload in parser.scripts:
        structured = json.loads(payload)
        require(
            "https://piyushkapoor.me/" in json.dumps(structured),
            "JSON-LD missing canonical domain",
        )

    ET.parse(SITE / "sitemap.xml")
    json.loads((SITE / "site.webmanifest").read_text(encoding="utf-8"))
    require(
        (SITE / "CNAME").read_text(encoding="utf-8").strip()
        == "piyushkapoor.me",
        "unexpected CNAME",
    )


if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, json.JSONDecodeError, ET.ParseError) as error:
        print(f"site validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("site validation passed")
