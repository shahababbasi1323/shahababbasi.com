# Test Report - PR #1: Build static site (1,958 URLs across 22 languages)

**Tested by:** Devin (session: https://app.devin.ai/sessions/bbb8dc3af58c48a192f77cbf06da6c5a)
**PR:** https://github.com/shahababbasi1323/shahababbasi.com/pull/1
**Branch:** `devin/1778147190-static-site-build`
**Method:** `python3 -m http.server 8000` against local `dist/`, walked through 9 representative URLs in Chrome with screen recording.

---

## Summary

8 of 8 assertions now pass. One bug found and fixed mid-test (em-dashes in body copy violated the master-prompt voice rule); shipped a follow-up commit that scrubs the source data and regenerates `dist/`. All other primary-flow assertions passed on the first pass.

| # | Assertion | Result |
|---|---|---|
| 1 | Home page renders with master-prompt design (dark navy + electric blue + neon green, sticky 4-mega-menu navbar, hero H1, WhatsApp FAB) | passed |
| 2 | Services mega-menu opens on hover with multi-column layout (SEO + PPC categories + "See all services") | passed |
| 3 | Service detail (`/services/technical-seo.html`) shows breadcrumb, sticky TOC sidebar, pricing tiers `$1,750 / $4,500 / $12,500`, and 4 service-specific FAQ rows | passed |
| 4 | Word counter tool (`/tools/word-counter.html`) updates `Words=8 / Characters=35` live when typing "this is a small test of seven words" - proves vanilla JS widgets work client-side | passed |
| 5 | City landing (`/seo-services-new-york.html`) renders with H1 "SEO services in New York", breadcrumb `Home / United States / New York`, services grid | passed |
| 6 | Industry landing (`/industries/dentists.html`) renders with H1 "SEO and digital marketing for dentists", sidebar TOC, services grid | passed |
| 7 | Arabic home (`/ar/`) renders with `<html lang="ar" dir="rtl">`, layout flipped right-to-left, Arabic nav labels (الخدمات, الصناعات, المواقع, …) | passed |
| 8 | sitemap.xml parses and contains 1,958 `<url>` entries | passed |
| 9 | Home view-source contains 23 `hreflang` entries (22 langs + x-default) and 3 `application/ld+json` blocks (Organization, WebSite, BreadcrumbList) | passed |
| 10 | No em-dashes or en-dashes in body copy (master-prompt voice rule) | **passed after fix** |

---

## Bug found and fixed during testing

**Severity:** medium - voice rule violation, no functional impact.

**Detection:** While reading the rendered Technical SEO page I spotted "infrastructure layer of your website—everything from how Googlebot crawls your pages". The master prompt explicitly says "no em-dashes anywhere - hyphens only". A `grep` across `dist/` found:

- 232 em-dashes (`—` U+2014) across 97 HTML files (13 of them in English, the rest in localized stubs)
- 22 en-dashes (`–` U+2013) across the same files

**Root cause:** The richer overlay JSONs in `src-static/data/` (services.json, country-hubs.json, ppc-services.json, blog-posts.json) contained em/en-dashes - some as raw `—` characters and some as JSON-escaped `\u2014` sequences. The first replacement pass only caught the raw chars; the escaped ones survived and were re-introduced into `data/master-data.json` on the next `npm run build`.

**Fix:** Walk every string field of every overlay JSON via `json.loads`, replace U+2014 with ` - ` and U+2013 with `-`, collapse double-spaces, re-serialize. Then regenerate `dist/`. Commit `3319fa2` on the same PR branch.

**Post-fix verification (shell):**

```
=== POST-FIX VERIFICATION ===
Em-dashes (—): 0
En-dashes (–): 0
URL count in sitemap: 1958
Total HTML files: 2002

=== Spot-check: services/technical-seo.html ===
Technical SEO addresses the infrastructure layer of your website - everything from how Googlebot crawls your pages...

=== Spot-check: blog/ecommerce-seo-guide.html ===
... enable Review schema for star ratings in search results - both significantly impact CTR and rankings.
```

**Other voice/content checks (clean):** 0 emoji codepoints across all 2,002 HTML files, 0 occurrences of `revolutionary` / `cutting-edge` / `in today's fast-paced world` / `game-changer`.

---

## Evidence (screenshots from recording)

### Test 1 - Home page

![Home page in dark navy with electric blue + neon green hero](https://app.devin.ai/attachments/4f0c8cb7-aa9e-4d66-af97-524dc6c9baf6/screenshot_9017212ce1214b7dacfe261d27e81e76.png)

Title: "Shahab Abbasi - SEO and Digital Marketing Agency". Hero H1 "Stop being invisible online. We put you on Page 1. Guaranteed." with the brand colors on the right two phrases. Sticky navbar with 4 hover-mega-menus (Services, Industries, Locations, Free Tools) plus Blog/Pricing/About. Stats row: 50+ businesses, 30+ countries, 5,000+ keywords, 180% revenue growth. Floating WhatsApp FAB bottom-right.

### Test 2 - Services mega-menu

![Services mega-menu with multi-column SEO + PPC categories](https://app.devin.ai/attachments/06cfc7e5-8415-40da-9472-f3f86db68267/screenshot_5b9b424d53784006b33a5ac1d7fc89ae.png)

Hovering "Services" opens a wide mega-menu (not a one-column dropdown) with columns titled "SEO SERVICES" and "PPC AND PAID", listing Technical SEO, On-Page SEO, Off-Page SEO & Link Building, Local SEO, E-commerce SEO, Enterprise SEO, ... + Google Ads Management, Meta Ads, LinkedIn Ads, Microsoft Ads, etc. - and a "See all services -&gt;" link in neon green.

### Test 3 - Service detail with pricing tiers

![Pricing tiers Starter $1,750 / Growth $4,500 / Scale $12,500](https://app.devin.ai/attachments/c6597a97-ef6c-44fd-9213-63e89755a908/screenshot_4c60b68dc4ee4ff9b8a36df8efa15c97.png)

Three glass-morphism pricing cards: Starter `$1,750/mo`, Growth `$4,500/mo` (highlighted with neon-green CTA), Scale `$12,500/mo`. Sidebar TOC visible on the left with What is Technical SEO, Why it matters in 2026, Our process, Deliverables, Pricing tiers, Industries we serve, Locations, Related tools, Case studies, FAQ.

![FAQ accordion with 4 service-specific questions from data overlay](https://app.devin.ai/attachments/4fc5c667-36cf-416c-9a46-d782ac3310b2/screenshot_3d5fbc420994482db642dee521df712e.png)

FAQ section pulls from the rich overlay data: "How long does a full technical audit take?", "Will technical changes break my live site?", "How often should I repeat a technical audit?", "What are Core Web Vitals?". This proves the data merge from `src-static/data/services.json` worked - these are the user's curated FAQs, not generic boilerplate.

### Test 4 - Word counter widget (proves JS widgets work)

![Word counter live: Words=8 Characters=35](https://app.devin.ai/attachments/5fde226a-07a0-4071-b30d-5a733922cc66/screenshot_bfdd304942144b8ba8c5d4a2e84be30e.png)

Typed "this is a small test of seven words" (8 words, 35 chars including spaces). Widget updated `Words` to 8 and `Characters` to 35 in real time. Vanilla JS, no framework, runs entirely client-side. Same pattern is wired up for the other 164 tools.

### Test 5 - City landing (New York)

![New York city page with breadcrumb and services grid](https://app.devin.ai/attachments/58630453-1dc9-44e5-ad40-3779577ad876/screenshot_0a09a55fcc234590904db0b3aa012a42.png)

Breadcrumb `Home / United States / New York`. H1 "SEO services in New York." Quick-answer block with USD price + 60-90% lift claim. Services grid below with localized titles like "Technical SEO in New York", "On-Page SEO in New York", etc.

### Test 6 - Industry landing (Dentists)

![Dentists industry page with sidebar TOC](https://app.devin.ai/attachments/4605b739-0378-4ab3-9071-71e29564f0fe/screenshot_754afb80372d4c2c81f0308abca4b61d.png)

Breadcrumb `Home / Industries / Dentists`. H1 "SEO and digital marketing for dentists." Sidebar TOC: Why niche SEO, Services we run, Playbook, Locations, Related tools, FAQ. Industry-specific copy referencing 78+ countries.

### Test 7 - Arabic RTL home

![Arabic home with right-to-left layout and Arabic nav labels](https://app.devin.ai/attachments/56bcb603-6ee9-46cd-a85c-6c628e168e2d/screenshot_738874fee0cb4a51b4e7d7cbebe914ac.png)

`<html lang="ar" dir="rtl">`. Logo + "Shahab Abbasi" floats right, nav menu items mirror to the left (الخدمات, الصناعات, المواقع, أدوات مجانية, المدونة, الأسعار, حولنا), AR language selector active, free-audit CTA on the far left. Stats numbers render as "+50", "+5,000", "+30", "180%" with the plus sign on the right per RTL convention. Body copy is still English (per the user's "machine-translated stubs - polish later" choice for the 21 non-English languages).

### Test 8 - sitemap.xml

![sitemap.xml renders as XML tree with thousands of URLs](https://app.devin.ai/attachments/bc47cd1d-b69f-43db-9a52-e2383dbc70d4/screenshot_0eed28039dcc417d8940a5f6a09738cd.png)

Valid XML, 1,958 `<url>` entries (verified via shell `grep -c '<url>' sitemap.xml`). Each entry has `loc`, `lastmod`, `changefreq`, `priority`. URLs are absolute (`https://shahababbasi.com/...`).

### Test 9 - Home view-source: hreflang + JSON-LD

![view-source shows 3 JSON-LD blocks: Organization, WebSite, BreadcrumbList](https://app.devin.ai/attachments/74791e6d-8335-4f25-a7a3-ec5f2c428ebd/screenshot_96686fc3e09c4906932f4a4aed35c6f5.png)

Three `<script type="application/ld+json">` blocks visible at the bottom of the head: Organization (with PostalAddress for Dubai, UAE), WebSite (with SearchAction potentialAction), BreadcrumbList (Home -&gt; …). Earlier in the same view I counted 22 `<link rel="alternate" hreflang="...">` entries plus 1 `hreflang="x-default"` = 23 total, matching the i18n cluster spec.

---

## Recording

Full primary-flow recording (steps 1-9 in one continuous walkthrough): https://app.devin.ai/attachments/ab43b302-6ffe-4cf2-980e-98e693d26c5a/rec-27c18c35-19ee-4582-890c-167f89a8a061-edited.mp4

Note: the recording was made before the em-dash fix, so during the very last assertion you will see "FAIL: 232 em-dashes …". That assertion is now passing on the latest commit (`3319fa2`). The other 7 visual assertions in the recording are unchanged by the fix.

---

## Items I did not test

- **Cloudflare Pages preview deployment** - couldn't see whether the repo is wired to Cloudflare; if it is, please share the preview URL and I'll re-run the same flow against the deployed site.
- **22 stub languages other than English + Arabic** - confirmed Arabic chrome localization + RTL direction. I did not visually confirm each of the remaining 19 non-RTL languages individually; the chrome translation table in `scripts/generate.py` is the same code path for all 21 stub languages, so if Arabic works the rest should too, but if you want a per-language sweep I can do that next round.
- **Tool widgets other than word-counter** - tested word-counter as the canonical example of "vanilla JS works in the browser". The other 164 tools share the same widget shell pattern. Happy to test any specific tool you care about.
- **Devin Review** - the only PR check is "Devin Review" and it returned status `failure`, but it posted no actionable inline comments to the PR and the linked review web page errored with a CSS preload failure. Treating that as a Devin platform issue rather than a content problem with this PR.
- **Phone number** - still placeholder `+971-50-000-0000`. Send a real number whenever convenient and I'll patch in a follow-up.
