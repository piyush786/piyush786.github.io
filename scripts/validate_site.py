from __future__ import annotations

import json
import struct
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
        self.id_values: list[str] = []
        self.local_refs: list[str] = []
        self.fragments: list[str] = []
        self.meta: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.scripts: list[tuple[dict[str, str], str]] = []
        self.images: list[dict[str, str]] = []
        self._json_attrs: dict[str, str] | None = None
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.add(values["id"])
            self.id_values.append(values["id"])

        if tag == "meta":
            self.meta.append(values)
        if tag == "link":
            self.links.append(values)

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
    duplicate_ids = sorted(
        value for value in parser.ids if parser.id_values.count(value) > 1
    )
    require(not duplicate_ids, f"duplicate ids: {duplicate_ids}")
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

    require('class="no-js"' in html, "document must expose a no-js fallback")
    require(
        'classList.replace("no-js", "js")' in html,
        "document must enable enhanced navigation before CSS loads",
    )

    css = (SITE / "assets/css/styles.css").read_text(encoding="utf-8")
    for token in (
        "#e8dcc8",
        "#113d37",
        "#1d2624",
        "#d89b43",
        "#f6f0e6",
        "#7a4c0c",
    ):
        require(token in css.lower(), f"missing palette token: {token}")
    for contract in (
        "prefers-reduced-motion",
        ":focus-visible",
        "@media (max-width: 900px)",
        ".project-story",
        ".system-map",
        ".no-js .main-nav",
        "max-height: calc(100dvh - 84px)",
        "overflow-y: auto",
        "box-shadow: 0 0 0 6px var(--emerald-deep)",
    ):
        require(contract in css, f"missing CSS contract: {contract}")

    javascript = (SITE / "assets/js/main.js").read_text(encoding="utf-8")
    for contract in (
        "aria-expanded",
        "aria-controls",
        "Close navigation",
        "Escape",
        "aria-current",
        "IntersectionObserver",
        "site-year",
        "(max-width: 900px)",
    ):
        require(
            contract in (html + javascript),
            f"missing navigation contract: {contract}",
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

    for asset in (
        "assets/images/piyush-kapoor-640.jpg",
        "assets/images/piyush-kapoor-960.jpg",
    ):
        require((SITE / asset).exists(), f"missing generated asset: {asset}")

    social_card = SITE / "assets/images/og-portfolio.png"
    if social_card.exists():
        require(
            "assets/images/og-portfolio.png" in html,
            "social metadata must use the accepted portfolio card",
        )
        with social_card.open("rb") as image_file:
            signature = image_file.read(24)
        require(signature[:8] == b"\x89PNG\r\n\x1a\n", "social card is not PNG")
        width, height = struct.unpack(">II", signature[16:24])
        require((width, height) == (1200, 630), "social card must be 1200x630")
    else:
        require(
            'property="og:image"' not in html
            and 'name="twitter:image"' not in html,
            "invalid fallback social image metadata remains",
        )

    require(parser.scripts, "missing JSON-LD")
    meta_by_name = {
        item["name"]: item.get("content", "")
        for item in parser.meta
        if item.get("name")
    }
    meta_by_property = {
        item["property"]: item.get("content", "")
        for item in parser.meta
        if item.get("property")
    }
    links_by_rel = {
        item["rel"]: item.get("href", "")
        for item in parser.links
        if item.get("rel")
    }
    require(
        links_by_rel.get("canonical") == "https://piyushkapoor.me/",
        "canonical URL is missing or incorrect",
    )
    require(bool(meta_by_name.get("description")), "meta description is missing")
    require(meta_by_name.get("theme-color") == "#113d37", "theme color is incorrect")
    for name in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
        require(bool(meta_by_name.get(name)), f"missing metadata: {name}")
    for name in ("og:type", "og:url", "og:title", "og:description", "og:image", "og:image:width", "og:image:height"):
        require(bool(meta_by_property.get(name)), f"missing metadata: {name}")
    require(meta_by_property.get("og:url") == "https://piyushkapoor.me/", "Open Graph URL is incorrect")
    require(meta_by_property.get("og:image:width") == "1200", "Open Graph width is incorrect")
    require(meta_by_property.get("og:image:height") == "630", "Open Graph height is incorrect")

    structured_types: set[str] = set()
    for _, payload in parser.scripts:
        structured = json.loads(payload)
        require(
            "https://piyushkapoor.me/" in json.dumps(structured),
            "JSON-LD missing canonical domain",
        )
        graph = structured.get("@graph", [structured])
        structured_types.update(
            item.get("@type", "") for item in graph if isinstance(item, dict)
        )
    require(
        {"Person", "ProfilePage", "WebSite"} <= structured_types,
        "JSON-LD is missing required schema types",
    )

    ET.parse(SITE / "sitemap.xml")
    require(
        "2026-07-10"
        in (SITE / "sitemap.xml").read_text(encoding="utf-8"),
        "sitemap date is stale",
    )
    manifest = json.loads((SITE / "site.webmanifest").read_text(encoding="utf-8"))
    require(manifest.get("theme_color") == "#113d37", "manifest theme color is incorrect")
    require(manifest.get("background_color") == "#e8dcc8", "manifest background color is incorrect")
    for icon in manifest.get("icons", []):
        require((SITE / icon["src"]).exists(), f"manifest icon is missing: {icon['src']}")
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
