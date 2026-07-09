# Piyush Kapoor Personal Portfolio Redesign

Date: 2026-07-10

## Objective

Redesign `piyushkapoor.me` as a polished, one-page personal portfolio for Piyush Kapoor. The page must communicate senior technical leadership clearly to recruiters, hiring managers, peers, and people evaluating Piyush's individual experience. It must not read like an agency website, a services catalogue, or a sales funnel.

Success means a visitor can understand Piyush's role, domain depth, leadership scope, selected work, career history, and contact options in a short scan, while a deeper read reveals credible architecture and delivery experience.

## Audience and positioning

Primary audiences:

- Technical Lead, Engineering Lead, Solution Architect, and senior full-stack hiring teams.
- Industry peers and professional contacts evaluating Piyush's individual background.
- Organizations considering Piyush personally for a leadership opportunity or focused advisory engagement.

The site positions Piyush as a Technical Lead in Riyadh who has spent more than 12 years delivering secure banking, payments, insurance, B2B, mobile, web, and enterprise platforms.

The writing uses first-person singular language. It avoids agency phrases such as "our services," "our process," "book a consultation," and "we build." Calls to action are personal: view selected work, download the resume, open LinkedIn, send an email, or connect.

## Information architecture

The site remains one semantic HTML page with these sections:

1. **Hero** — name, Technical Lead role, Riyadh location, a concise leadership statement, portrait, and resume/LinkedIn actions.
2. **Career proof** — 12+ years, 15 integrations, 8 engineers led, and 10 banking/payment journeys, presented once without repetition elsewhere.
3. **Selected work** — three substantial portfolio stories: SAIB Travel Application, YES IRIS Mobile Banking, and AU Merchant Banking.
4. **More selected work** — compact entries for YES API HUB, FWD Group, and MAAK.
5. **Leadership profile** — a merged About and Delivery Model narrative covering architecture decisions, cross-functional delivery, mentoring, release ownership, and production stability.
6. **Experience** — the three Technical Lead roles receive the most space; earlier positions are compressed into a concise career foundation timeline.
7. **Capabilities** — Architecture, Banking Platforms, Web and Mobile Delivery, and Engineering Leadership, with supporting technologies rather than an undifferentiated keyword list.
8. **Credentials** — education and direct links to the resume and LinkedIn profile. Certifications appear only if documented later.
9. **Contact** — a personal "Let's connect" close with email, LinkedIn, telephone links, and resume access.

Sticky navigation links to Selected Work, Leadership, Experience, Capabilities, and Contact. Existing public section IDs are retained where practical so old fragment links continue to work.

## Content model

### Hero

The hero leads with personal identity and leadership, not a client pitch. The core message is equivalent to:

> I lead secure banking platforms from architecture to production.

Supporting copy names Java Spring Boot, React Native, React.js, banking, payments, and enterprise delivery without becoming a keyword string.

Primary actions are "View selected work" and "Download resume." LinkedIn remains an immediately discoverable secondary action.

### Featured portfolio stories

Each featured story uses the same structure:

- Context: what kind of platform or customer journey it supported.
- My role: Piyush's specific leadership and implementation responsibility.
- Platform shape: mobile/web clients, services, APIs, integrations, and data technologies.
- Delivery scope: verified team, journey, service, or integration context when supported by the current site or resume.
- Contribution: architecture, technical direction, coordination, release, or production ownership.
- Technology tags: a short, curated list.

The stories do not invent revenue, conversion, latency, user-count, or percentage improvements. Where banking confidentiality prevents public screenshots or internal details, a short confidentiality note explains that the portfolio uses abstract system maps and verified delivery context.

### Additional work and experience

Additional projects remain concise and clearly subordinate to the three featured stories. Recent Technical Lead experience is detailed; older experience establishes career progression without repeating generic duties.

MAAK remains an additional project because it is already part of the public website, but it is not promoted into a deep featured story without further supporting detail. Claims found only in one source are not expanded beyond the existing wording.

## Visual design

The approved direction is **Riyadh Product Casebook**, adapted from a product/client casebook into a personal leadership portfolio.

### Palette

- Warm sand: `#E8DCC8`
- Deep emerald: `#113D37`
- Charcoal: `#1D2624`
- Saffron accent: `#D89B43`
- Soft cream surface: approximately `#F6F0E6`

Final shades may be adjusted slightly to meet WCAG AA contrast, while retaining this visual character.

### Typography and composition

- Editorial serif display headings paired with a clean system sans-serif for body copy and controls.
- Large but calm headlines with balanced line lengths and tighter mobile scaling than the current site.
- A portrait-led hero using the existing photo with a deliberate crop that emphasizes Piyush rather than the landscape.
- Sweeping asymmetrical CSS shapes and fine line details inspired by architecture and customer journeys.
- Fewer, larger project panels instead of repeated equal-weight cards.
- Generous whitespace, clear reading rhythm, and strong section contrast.

No model-authored SVG illustrations are used. Technical visuals are built from accessible HTML and CSS primitives.

## Responsive behavior

The desktop hero uses an asymmetric text/portrait composition. At tablet widths, the layout becomes a balanced two-row composition. On phones, content becomes a single column with the identity, positioning, actions, metrics, and portrait ordered for fast scanning.

The design must work at 320px and above, at 200% zoom, in short landscape viewports, and with long text wrapping. Buttons remain touch-friendly and do not rely on hover. Navigation must remain usable if JavaScript is unavailable.

## Interaction design

Interaction stays restrained:

- Sticky navigation with active-section indication.
- Accessible mobile menu with `aria-controls`, accurate open/close labels, Escape handling, outside-click dismissal, and sensible focus behavior.
- Subtle project and link hover treatments.
- Optional scroll reveals that never hide content when JavaScript is disabled.
- Smooth scrolling only when the user has not requested reduced motion.

There are no modal project pages, carousels, contact forms, dashboards, or application-like state.

## Technical architecture

The deployment remains a dependency-free static GitHub Pages site:

- `portfolio-site/index.html` owns semantic structure, content, metadata, and structured data.
- `portfolio-site/assets/css/styles.css` owns readable, formatted visual and responsive styles.
- `portfolio-site/assets/js/main.js` owns progressive navigation enhancement only.
- Image assets live under `portfolio-site/assets/images/`.
- The existing resume path remains valid.
- `CNAME`, `.nojekyll`, `robots.txt`, `sitemap.xml`, `site.webmanifest`, and `.github/workflows/pages.yml` remain in the deployment flow.

No framework, package manager, backend, database, analytics service, or third-party form service is introduced.

## Metadata and assets

The redesign preserves and updates:

- Canonical URL and custom domain.
- Open Graph and X/Twitter metadata.
- Person, ProfilePage, and WebSite structured data.
- Sitemap modification date and manifest colors.
- Portrait alt text and intrinsic dimensions.
- A dedicated landscape social-preview image matching the finished palette and message.

The portrait receives responsive formats or sizes where tooling supports them, with the current JPEG retained as a dependable fallback.

## Accessibility and failure behavior

- Semantic landmarks, heading order, lists, links, buttons, and the skip link remain intact.
- Text, controls, focus indicators, and meaningful visual details meet WCAG AA contrast.
- Keyboard users can open, use, and close navigation without becoming trapped.
- Active navigation uses visual styling and `aria-current` where appropriate.
- Motion honors `prefers-reduced-motion`.
- Images have descriptive alternative text, dimensions, and graceful layout behavior if unavailable.
- With JavaScript disabled, navigation links, content, email, phone, LinkedIn, and resume access still work.
- There is no form submission state or network-dependent content to fail.

## Validation

Before completion, validate:

- HTML structure and metadata parse correctly.
- JavaScript syntax is valid.
- Local files, fragment links, resume links, manifest references, and sitemap references resolve.
- Structured data is valid JSON and uses the canonical domain.
- No stale asset-version strings or removed section styles remain.
- Keyboard navigation, focus visibility, mobile menu behavior, and reduced-motion behavior are correct.
- Color contrast meets WCAG AA.
- Layout is checked at 320px, common phone/tablet widths, desktop, short landscape heights, and 200% zoom.
- A local HTTP smoke test serves the full site and key assets successfully.
- The GitHub Pages artifact path remains `portfolio-site/`.

## Delivery boundary

This implementation changes the local repository and verifies the result. Publishing or changing GitHub Pages domain settings is separate unless the user explicitly requests it. The existing workflow is preserved so a later push to `main` can deploy the verified site.
