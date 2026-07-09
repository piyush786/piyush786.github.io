# Personal Portfolio Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished, responsive one-page personal portfolio for Piyush Kapoor using the approved Riyadh Product Casebook direction while preserving the existing GitHub Pages deployment.

**Architecture:** Keep the existing dependency-free static architecture. `portfolio-site/index.html` owns semantic content and metadata, `portfolio-site/assets/css/styles.css` owns the visual system and responsive layout, and `portfolio-site/assets/js/main.js` progressively enhances navigation. A Python standard-library validator checks content, local assets, metadata, accessibility hooks, and deployment references before GitHub Pages uploads `portfolio-site/`.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript, Python 3 standard library, GitHub Actions, GitHub Pages.

## Global Constraints

- The site is a personal portfolio, never an agency site or services catalogue.
- The approved palette starts from sand `#E8DCC8`, emerald `#113D37`, charcoal `#1D2624`, saffron `#D89B43`, and cream `#F6F0E6`; adjustments are allowed only to meet WCAG AA.
- Use first-person singular copy and retain only claims supported by the existing site or resume.
- Keep a single page, no framework, no package manager, no backend, no form service, and no analytics dependency.
- Preserve `portfolio-site/` as the deployed artifact, the custom domain, `.nojekyll`, the current resume path, canonical URLs, sitemap, manifest, and JSON-LD.
- Preserve or provide compatible fragment targets for `#about`, `#projects`, `#experience`, `#stack`, and `#contact`.
- No model-authored SVG illustrations; visual system maps use semantic HTML and CSS.
- JavaScript is progressive enhancement: all content and primary links work when it is disabled.
- Meet WCAG AA contrast, support keyboard operation and `prefers-reduced-motion`, and work at 320px, 200% zoom, and short landscape heights.

---

## File Responsibility Map

- `portfolio-site/index.html`: page content, semantic landmarks, navigation, structured data, social metadata, responsive image markup.
- `portfolio-site/assets/css/styles.css`: design tokens, typography, layout, casebook components, system-map visuals, focus/motion/mobile rules.
- `portfolio-site/assets/js/main.js`: accessible menu state, outside/Escape dismissal, active navigation, current year.
- `portfolio-site/assets/images/piyush-kapoor-640.jpg`: responsive portrait source for small screens.
- `portfolio-site/assets/images/piyush-kapoor-960.jpg`: responsive portrait source for medium screens.
- `portfolio-site/assets/images/og-portfolio.png`: accepted 1200×630 social-preview image matching the final design; omitted if generated text cannot be validated.
- `portfolio-site/site.webmanifest`: updated theme/background colors and icon metadata.
- `portfolio-site/sitemap.xml`: canonical URL and redesign modification date.
- `.github/workflows/pages.yml`: run static validation before artifact upload.
- `scripts/validate_site.py`: dependency-free repository validation; never included in the deployed artifact.

---

### Task 1: Semantic portfolio content and contract validator

**Files:**

- Create: `scripts/validate_site.py`
- Modify: `portfolio-site/index.html`

**Interfaces:**

- Consumes: current resume at `portfolio-site/assets/cvs/Piyush_Kapoor_Tech_Lead_Resume.pdf` and current canonical domain `https://piyushkapoor.me/`.
- Produces: stable IDs `top`, `projects`, `about`, `leadership`, `experience`, `stack`, `credentials`, and `contact`; CSS class contracts used by Task 2; `.nav-toggle`, `.main-nav`, and `.site-year` hooks used by Task 3.

- [ ] **Step 1: Write the failing static-site validator**

Create `scripts/validate_site.py` with Python standard-library checks that:

```python
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
        self.scripts: list[tuple[dict[str, str], str]] = []
        self._json_attrs: dict[str, str] | None = None
        self._json_parts: list[str] = []
        self.images: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.add(values["id"])
        if tag in {"a", "link", "script", "img", "source"}:
            for key in ("href", "src", "srcset"):
                if values.get(key):
                    self.local_refs.append(values[key])
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

    required_ids = {"top", "projects", "about", "leadership", "experience", "stack", "credentials", "contact"}
    require(required_ids <= parser.ids, f"missing section ids: {sorted(required_ids - parser.ids)}")
    for phrase in ("I lead secure banking platforms", "Selected work", "Technical Lead in Riyadh", "Let's connect"):
        require(phrase.lower() in html.lower(), f"missing personal portfolio phrase: {phrase}")
    for forbidden in ("our services", "book a consultation", "we build", "our clients"):
        require(forbidden not in html.lower(), f"agency language present: {forbidden}")

    local_refs: set[str] = set()
    for ref in parser.local_refs:
        for candidate in ref.split(","):
            candidate = candidate.strip().split()[0]
            parsed = urlparse(candidate)
            if not candidate or parsed.scheme or candidate.startswith(("#", "mailto:", "tel:")):
                continue
            local_refs.add(parsed.path)
    missing = sorted(ref for ref in local_refs if ref and not (SITE / ref).exists())
    require(not missing, f"missing local assets: {missing}")

    for image in parser.images:
        require(bool(image.get("alt")), f"image missing alt: {image.get('src')}")
        require(bool(image.get("width")) and bool(image.get("height")), f"image missing dimensions: {image.get('src')}")

    require(parser.scripts, "missing JSON-LD")
    for _, payload in parser.scripts:
        structured = json.loads(payload)
        require("https://piyushkapoor.me/" in json.dumps(structured), "JSON-LD missing canonical domain")

    ET.parse(SITE / "sitemap.xml")
    json.loads((SITE / "site.webmanifest").read_text(encoding="utf-8"))
    require((SITE / "CNAME").read_text(encoding="utf-8").strip() == "piyushkapoor.me", "unexpected CNAME")


if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, json.JSONDecodeError, ET.ParseError) as error:
        print(f"site validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("site validation passed")
```

- [ ] **Step 2: Run the validator and confirm the current site fails**

Run: `python3 scripts/validate_site.py`

Expected: exit code 1 with `site validation failed: missing section ids` because the current page has no `leadership` or `credentials` section.

- [ ] **Step 3: Replace the page with the approved personal-portfolio structure**

Rewrite `portfolio-site/index.html` with this exact page contract:

- A `Skip to content` link targets `<main id="main">`.
- `.site-header` contains the `PK / Piyush Kapoor` identity, `.nav-toggle`, and `<nav id="main-navigation" class="main-nav">`.
- `#top.hero` contains the approved eyebrow, headline, summary, two actions, portrait, and CSS decorative elements.
- `.proof-strip[aria-label="Career highlights"]` contains the four approved proof values.
- `#projects.section.selected-work` contains the three featured `.project-story` articles and their accessible CSS system maps.
- `.more-work[aria-labelledby="more-work-title"]` contains YES API HUB, FWD Group Insurance Platform, and MAAK Application.
- `#about.section.about-section` introduces Piyush's personal leadership profile.
- `#leadership.section.leadership-section` contains Architecture direction, Cross-functional delivery, and Production ownership principles.
- `#experience.section.experience-section` contains the six-role chronology, with the first three roles visually emphasized.
- `#stack.section.capabilities-section` contains Architecture, Banking Platforms, Web and Mobile Delivery, and Engineering Leadership groups.
- `#credentials.section.credentials-section` contains Guru Nanak Dev Engineering College, the resume link, and LinkedIn.
- `#contact.section.contact-section` contains the exact heading `Let's connect.` plus email, LinkedIn, both current phone links, and resume.
- `.site-footer` contains Piyush Kapoor, `<span class="site-year">2026</span>`, and fragment navigation.
- `<script src="assets/js/main.js" defer></script>` is the last body child.

Use this exact hero positioning:

```html
<p class="eyebrow">Technical Lead · Riyadh, Saudi Arabia</p>
<h1>I lead secure banking platforms from <em>architecture</em> to production.</h1>
<p class="hero-summary">I’m Piyush Kapoor, a Technical Lead with 12+ years shaping Java Spring Boot services, React Native apps, React.js platforms, secure APIs, and production delivery across banking, payments, insurance, and enterprise systems.</p>
<a class="button button-primary" href="#projects">View selected work</a>
<a class="button button-secondary" href="assets/cvs/Piyush_Kapoor_Tech_Lead_Resume.pdf" download>Download resume</a>
```

Show the four proof values only once: `12+ years`, `15 integrations`, `8 engineers led`, and `10 banking journeys`.

Featured projects must be SAIB Travel Application, YES IRIS Mobile Banking Platform, and AU Merchant Banking Application. Each uses child blocks with labels `Context`, `My role`, `Platform`, and `Contribution`, plus a short technology list. Additional work must list YES API HUB, FWD Group Insurance Platform, and MAAK Application. Keep all descriptions within the claims in the approved design specification.

The contact heading is `Let's connect.` and its copy addresses opportunities and professional conversation personally; it does not offer agency services.

- [ ] **Step 4: Run semantic validation**

Run: `python3 scripts/validate_site.py`

Expected: `site validation passed`.

- [ ] **Step 5: Check the HTML patch and commit**

Run: `git diff --check && git diff --stat`

Expected: no whitespace errors; `index.html` and `scripts/validate_site.py` are listed.

```bash
git add portfolio-site/index.html scripts/validate_site.py
git commit -m "feat: restructure portfolio content"
```

---

### Task 2: Riyadh Product Casebook visual system

**Files:**

- Modify: `scripts/validate_site.py`
- Modify: `portfolio-site/assets/css/styles.css`

**Interfaces:**

- Consumes: the semantic class and ID contracts produced by Task 1.
- Produces: responsive visual rules and CSS hooks for Task 3; no JavaScript-dependent visibility.

- [ ] **Step 1: Extend the validator with visual/accessibility contracts**

Add these assertions inside `validate()` after reading `styles.css`:

```python
css = (SITE / "assets/css/styles.css").read_text(encoding="utf-8")
for token in ("#e8dcc8", "#113d37", "#1d2624", "#d89b43", "#f6f0e6"):
    require(token in css.lower(), f"missing palette token: {token}")
for contract in ("prefers-reduced-motion", ":focus-visible", "@media (max-width: 760px)", ".project-story", ".system-map"):
    require(contract in css, f"missing CSS contract: {contract}")
```

- [ ] **Step 2: Run the validator and confirm the old CSS fails**

Run: `python3 scripts/validate_site.py`

Expected: exit code 1 with `site validation failed: missing palette token: #e8dcc8`.

- [ ] **Step 3: Replace the stylesheet with readable casebook styles**

Rewrite `portfolio-site/assets/css/styles.css` as formatted source using these exact tokens and component contracts:

```css
:root {
  color-scheme: light;
  --sand: #e8dcc8;
  --emerald: #113d37;
  --charcoal: #1d2624;
  --saffron: #d89b43;
  --cream: #f6f0e6;
  --ink: #17322e;
  --muted: #596762;
  --line: rgba(17, 61, 55, 0.2);
  --white: #fffdf8;
  --max-width: 1180px;
  --shadow: 0 28px 70px rgba(17, 61, 55, 0.16);
}
```

Implement styles for: reset/base, skip link, sticky header, desktop/mobile navigation, asymmetric hero, CSS arch/circle decoration, portrait frame, proof strip, shared section headers, three `.project-story` layouts, `.system-map` with mobile/web/API/service/core nodes and connecting CSS lines, compact additional work, leadership principles, shortened experience timeline, capability columns, credentials, contact, footer, focus state, and motion preferences.

Desktop uses a two-column hero and asymmetric project stories. At `1050px`, large multi-column sections reduce to two columns. At `760px`, navigation becomes a button-controlled panel and all major content becomes one column. At `430px`, actions become full width. Define `@media (prefers-reduced-motion: reduce)` to disable smooth scrolling, transitions, and reveal transforms.

Do not hide page content by default. Scroll enhancement may add a class that transitions opacity/position only after the element is already readable.

- [ ] **Step 4: Run validation**

Run: `python3 scripts/validate_site.py`

Expected: `site validation passed`.

- [ ] **Step 5: Check and commit the visual system**

Run: `git diff --check && wc -l portfolio-site/assets/css/styles.css`

Expected: no whitespace errors and a readable multi-line stylesheet.

```bash
git add portfolio-site/assets/css/styles.css scripts/validate_site.py
git commit -m "feat: add Riyadh casebook visual system"
```

---

### Task 3: Accessible navigation enhancement

**Files:**

- Modify: `scripts/validate_site.py`
- Modify: `portfolio-site/assets/js/main.js`

**Interfaces:**

- Consumes: `.nav-toggle`, `#main-navigation`, `.main-nav a`, page section IDs, and `.site-year` from Task 1.
- Produces: `aria-expanded`, open/close accessible labels, `aria-current="location"`, Escape/outside-click dismissal, and current footer year.

- [ ] **Step 1: Add failing JavaScript contract checks**

Add to `validate()`:

```python
javascript = (SITE / "assets/js/main.js").read_text(encoding="utf-8")
for contract in ("aria-expanded", "aria-controls", "Close navigation", "Escape", "aria-current", "IntersectionObserver", "site-year"):
    require(contract in (html + javascript), f"missing navigation contract: {contract}")
```

- [ ] **Step 2: Run the validator and confirm the current script fails**

Run: `python3 scripts/validate_site.py`

Expected: exit code 1 mentioning `aria-controls` or `Close navigation`.

- [ ] **Step 3: Implement the complete progressive enhancement**

Replace `portfolio-site/assets/js/main.js` with an IIFE that:

```javascript
(() => {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector("#main-navigation");
  const links = [...document.querySelectorAll(".main-nav a[href^='#']")];
  const year = document.querySelector(".site-year");

  if (year) year.textContent = String(new Date().getFullYear());
  if (!toggle || !nav) return;

  const setMenu = (open, { restoreFocus = false } = {}) => {
    nav.classList.toggle("is-open", open);
    document.body.classList.toggle("nav-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    if (restoreFocus) toggle.focus();
  };

  toggle.addEventListener("click", () => {
    setMenu(toggle.getAttribute("aria-expanded") !== "true");
  });
  links.forEach((link) => link.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
      setMenu(false, { restoreFocus: true });
    }
  });
  document.addEventListener("click", (event) => {
    if (toggle.getAttribute("aria-expanded") === "true" && !nav.contains(event.target) && !toggle.contains(event.target)) {
      setMenu(false);
    }
  });

  if ("IntersectionObserver" in window) {
    const sections = links.map((link) => document.querySelector(link.hash)).filter(Boolean);
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        links.forEach((link) => {
          const active = link.hash === `#${entry.target.id}`;
          link.classList.toggle("is-active", active);
          if (active) link.setAttribute("aria-current", "location");
          else link.removeAttribute("aria-current");
        });
      }
    }, { rootMargin: "-35% 0px -55%", threshold: 0 });
    sections.forEach((section) => observer.observe(section));
  }
})();
```

Ensure the HTML toggle has `aria-controls="main-navigation"`, `aria-expanded="false"`, and `aria-label="Open navigation"`.

- [ ] **Step 4: Validate syntax and contracts**

Run:

```bash
node --check portfolio-site/assets/js/main.js
python3 scripts/validate_site.py
```

Expected: no output from `node --check`, then `site validation passed`.

- [ ] **Step 5: Commit navigation enhancement**

```bash
git add portfolio-site/index.html portfolio-site/assets/js/main.js scripts/validate_site.py
git commit -m "feat: improve accessible portfolio navigation"
```

---

### Task 4: Responsive and social assets plus metadata

**Files:**

- Create: `portfolio-site/assets/images/piyush-kapoor-640.jpg`
- Create: `portfolio-site/assets/images/piyush-kapoor-960.jpg`
- Create if accepted: `portfolio-site/assets/images/og-portfolio.png`
- Modify: `portfolio-site/index.html`
- Modify: `portfolio-site/site.webmanifest`
- Modify: `portfolio-site/sitemap.xml`
- Modify: `scripts/validate_site.py`

**Interfaces:**

- Consumes: final headline, palette, portrait crop, and metadata from Tasks 1–2.
- Produces: responsive portrait `srcset`, stable social-preview URL, updated theme colors and modification date.

- [ ] **Step 1: Add failing asset and metadata checks**

Add to `validate()`:

```python
for asset in ("assets/images/piyush-kapoor-640.jpg", "assets/images/piyush-kapoor-960.jpg"):
    require((SITE / asset).exists(), f"missing generated asset: {asset}")
social_card = SITE / "assets/images/og-portfolio.png"
if social_card.exists():
    require("assets/images/og-portfolio.png" in html, "social metadata must use the accepted portfolio card")
else:
    require('property="og:image"' not in html and 'name="twitter:image"' not in html, "invalid fallback social image metadata remains")
require("2026-07-10" in (SITE / "sitemap.xml").read_text(encoding="utf-8"), "sitemap date is stale")
```

- [ ] **Step 2: Run the validator and confirm missing assets fail**

Run: `python3 scripts/validate_site.py`

Expected: exit code 1 with `missing generated asset: assets/images/piyush-kapoor-640.jpg`.

- [ ] **Step 3: Create responsive portrait variants**

Run:

```bash
sips -Z 640 portfolio-site/assets/images/piyush-kapoor.jpeg --out portfolio-site/assets/images/piyush-kapoor-640.jpg
sips -Z 960 portfolio-site/assets/images/piyush-kapoor.jpeg --out portfolio-site/assets/images/piyush-kapoor-960.jpg
```

Expected: two valid JPEG files no larger than the original dimensions.

- [ ] **Step 4: Generate exactly one bespoke social card**

Use image generation once with this prompt:

```text
Create a complete 1200x630 social sharing card for Piyush Kapoor's personal Technical Lead portfolio. Use the Riyadh Product Casebook visual system: warm sand #E8DCC8, deep emerald #113D37, charcoal #1D2624, restrained saffron #D89B43, editorial serif heading with clean sans-serif labels, sweeping architectural arcs and fine journey lines. Include the exact text "Piyush Kapoor" and "Technical Lead · Banking platforms from architecture to production". This is an individual professional portfolio, never an agency advertisement. Keep the text highly legible at social-thumbnail size, no logos, no watermark, no fake UI, no additional names.
```

Inspect the result at full size. Accept it only if both required text strings are correct and readable. If the initial image is unusable, make one retry with the same palette and shorter exact text. Save the accepted output as `portfolio-site/assets/images/og-portfolio.png`; if both attempts are unusable, omit `og:image` and `twitter:image` instead of shipping incorrect text.

- [ ] **Step 5: Wire responsive images and metadata**

Use `srcset` values `assets/images/piyush-kapoor-640.jpg 640w`, `assets/images/piyush-kapoor-960.jpg 960w`, and `assets/images/piyush-kapoor.jpeg 1024w`. Point Open Graph and X/Twitter image metadata to `https://piyushkapoor.me/assets/images/og-portfolio.png` only if the image passed inspection. Set manifest `theme_color` to `#113D37`, `background_color` to `#E8DCC8`, and sitemap `<lastmod>` to `2026-07-10`.

- [ ] **Step 6: Validate and commit assets**

Run:

```bash
file portfolio-site/assets/images/piyush-kapoor-640.jpg portfolio-site/assets/images/piyush-kapoor-960.jpg
if [ -f portfolio-site/assets/images/og-portfolio.png ]; then file portfolio-site/assets/images/og-portfolio.png; fi
python3 scripts/validate_site.py
```

Expected: valid JPEG/JPEG/PNG descriptions, then `site validation passed`.

```bash
git add portfolio-site/assets/images portfolio-site/index.html portfolio-site/site.webmanifest portfolio-site/sitemap.xml scripts/validate_site.py
git commit -m "feat: add portfolio media and social metadata"
```

---

### Task 5: Deployment gate and final verification

**Files:**

- Modify: `.github/workflows/pages.yml`
- Modify: `scripts/validate_site.py`

**Interfaces:**

- Consumes: the complete static site and validator from Tasks 1–4.
- Produces: a deployment workflow that refuses to upload invalid site artifacts.

- [ ] **Step 1: Add the validator to GitHub Pages deployment**

Insert immediately after checkout in `.github/workflows/pages.yml`:

```yaml
      - name: Validate static portfolio
        run: python3 scripts/validate_site.py
```

Do not change `path: portfolio-site` or the existing Pages permissions/environment.

- [ ] **Step 2: Run the full local static checks**

Run:

```bash
python3 scripts/validate_site.py
node --check portfolio-site/assets/js/main.js
git diff --check
```

Expected: `site validation passed`, no JavaScript syntax output, and no whitespace errors.

- [ ] **Step 3: Run an HTTP smoke test**

Start: `python3 -m http.server 4173 --directory portfolio-site`

In a second shell run:

```bash
curl -fsS http://127.0.0.1:4173/ > /tmp/piyush-portfolio.html
curl -fsSI http://127.0.0.1:4173/assets/css/styles.css
curl -fsSI http://127.0.0.1:4173/assets/js/main.js
curl -fsSI http://127.0.0.1:4173/assets/cvs/Piyush_Kapoor_Tech_Lead_Resume.pdf
if [ -f portfolio-site/assets/images/og-portfolio.png ]; then curl -fsSI http://127.0.0.1:4173/assets/images/og-portfolio.png; fi
```

Expected: the page downloads and each asset responds `HTTP/1.0 200 OK`.

- [ ] **Step 4: Render visual checkpoints**

Open `http://127.0.0.1:4173/` in the in-app browser and capture the full page at exactly 1600×1000, 768×1024, and 390×844 viewports. Inspect all three captures for text clipping, horizontal overflow, broken portrait crops, unreadable contrast, menu overlap, and missing sections. At 390×844, open and close the menu with the button and Escape key. Fix observed problems in HTML/CSS/JS, then rerun Steps 2–4.

- [ ] **Step 5: Verify source and artifact boundaries**

Run:

```bash
git status --short
find portfolio-site -maxdepth 3 -type f -print | sort
```

Expected: only intended portfolio, validation, workflow, and documentation changes; no `.DS_Store`, `.superpowers`, temporary screenshots, or server output tracked.

- [ ] **Step 6: Commit the deployment gate and final fixes**

```bash
git add .github/workflows/pages.yml portfolio-site scripts/validate_site.py
git commit -m "ci: validate portfolio before deployment"
```

- [ ] **Step 7: Final verification from a clean status**

Run:

```bash
python3 scripts/validate_site.py
node --check portfolio-site/assets/js/main.js
git status --short --branch
```

Expected: all checks pass and the branch is clean ahead of `origin/main`. Do not push unless the user explicitly requests publishing.
