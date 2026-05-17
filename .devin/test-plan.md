# Test plan: PR #1 — static site for shahababbasi.com

PR: https://github.com/shahababbasi1323/shahababbasi.com/pull/1
Source of truth: `dist/` (served locally on port 8000 from this VM — same files that would deploy to Cloudflare Pages).

## What changed

Replaced the basic Node-based generator (~312 simple pages, white + purple/orange design) with a Python/Jinja2 generator that produces 1,958 URLs across 22 languages with the dark navy + electric blue + neon green design system, full JSON-LD, hreflang clusters, and working vanilla-JS tool widgets per the master prompt.

Code references:
- `scripts/generate.py:31` — output dir is `dist/`
- `scripts/generate.py:1024` — `render_tool` injects vanilla-JS widget HTML
- `scripts/generate.py:1015` — `render_city` adds `LocalBusiness` JSON-LD
- `scripts/generate.py:945` — `render_service` adds `Service` + `FAQPage` + `HowTo` JSON-LD
- `templates/_partials/head.html` — page-level JSON-LD anchors and hreflang loop
- `templates/_partials/header.html` — sticky navbar with 4 mega menus

A broken implementation here would manifest as: pages with the wrong (light/Lovable) design, missing JSON-LD blocks, missing hreflang, broken tool widgets, English chrome on the Arabic page, or non-RTL Arabic page.

## Primary flow (one continuous recording)

The reviewer should be able to watch the recording once and conclude "yep, the static site works as advertised". Browse a representative cross-section of page types and verify on-page evidence at each stop.

| # | URL | Action | Pass criteria |
|---|---|---|---|
| 1 | `http://localhost:8000/` | Load page | Background is dark navy (not white). Page title in tab reads `Shahab Abbasi - SEO and Digital Marketing Agency`. Hero H1 is visible. Sticky navbar shows 4 menu groups (Services, Industries, Locations, Free Tools). Floating WhatsApp button in bottom-right. |
| 2 | Same page | Hover navbar item "Services" | A mega-menu panel opens showing categories like "Technical SEO", "AI SEO", "Local SEO". Mega-menu must NOT be a single dropdown of plain text links. |
| 3 | `/services/technical-seo.html` | Click into Technical SEO | URL path is `/services/technical-seo.html`. H1 contains "Technical SEO that compounds revenue." Sidebar "On this page" sticky TOC visible on desktop. Pricing tiers section shows three glass cards (Starter $1,750/mo, Growth $4,500/mo, Scale $12,500/mo). FAQ accordion visible at bottom with at least 3 expandable questions. |
| 4 | `/tools/word-counter.html` | Navigate to a tool, type "this is a small test of seven words" into the `#wc-input` textarea | The `#wc-words` element updates to `8` and `#wc-chars` updates to a number ≥30. (If the JS is broken, both would stay at `0`.) |
| 5 | `/seo-services-new-york.html` | Open a city page | H1 contains "SEO services in New York" or similar. Breadcrumb shows `Home > United States > New York` (or matching country). |
| 6 | `/industries/dentists.html` | Open an industry page | H1 contains "dentists" wording. |
| 7 | `/ar/` | Open Arabic site | `<html lang="ar" dir="rtl">` (confirmed via DOM inspection / view-source). Nav labels are translated to Arabic (e.g. "الخدمات" for Services). Page chrome is mirrored RTL (logo on the right, hamburger/account on the left in mobile). |
| 8 | `/sitemap.xml` | Load sitemap | XML loads, contains `<loc>https://shahababbasi.com/</loc>` and at least 1,000 `<url>` entries (sanity-check that the full sitemap is being shipped, not a stub). |
| 9 | `/index.html` view-source | Open browser view-source | `<head>` contains exactly **23** `<link rel="alternate" hreflang="..."` entries (22 languages + x-default). Page contains at least 3 `<script type="application/ld+json">` blocks (Organization, WebSite, BreadcrumbList; many pages have more). |

## Cross-cutting assertions (verified via view-source / DOM, not visual)

These run during step 9 and the city/service stops to ensure SEO machinery isn't visually present but secretly broken:

- **Title length**: `<title>` of every visited page is between 10 and 70 characters.
- **Meta description**: `<meta name="description">` exists and is between 50 and 200 characters.
- **JSON-LD parses**: every `<script type="application/ld+json">` block on the home page parses as JSON (no trailing commas, no broken escaping).
- **No emojis / no em-dashes**: search visible body copy on home + service + city pages for `—` (em-dash) or any emoji codepoint. Expected count: 0.
- **CrawlerLinks block**: home page contains an element with class containing `sr-only` that holds at least 100 `<a href>` links (the hidden internal-link block).

## Out-of-scope (not testing)

- Cloudflare Pages live preview — not yet provisioned. Same `dist/` content is being tested locally; the only thing the live deploy adds is a CDN, which would not affect the on-page assertions above.
- Translation accuracy in non-English pages — per user's "machine-translated stubs" decision, only chrome (navbar/footer) is translated; bodies remain English. Plan only checks Arabic chrome + RTL direction, not body localization.
- Schema.org Validator — too slow and external. Local JSON parse is the proxy assertion.
- All 1,958 URLs — sampling a handful of representative types is enough to prove the generator works; the full set was already counted via `find dist -type f`.

## Recording

Single screen recording covering steps 1–9 above with `annotate_recording` markers at each step start.
