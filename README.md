# shahababbasi.com

Static HTML site for [shahababbasi.com](https://shahababbasi.com) - SEO Expert and Digital Marketing Strategist.

Pure HTML5 + Tailwind CDN + vanilla JavaScript. No React, no Vue, no build-time JS dependencies in the deployed artifact - the only thing the browser downloads is HTML, the Tailwind CDN, and small inline scripts.

## What's in the box

| Folder | What it is | Deployed? |
|---|---|---|
| `dist/` | Generated static site - ~2,000 HTML files across 22 languages | YES |
| `templates/` | Jinja2 templates (build-time only) | no |
| `scripts/` | Python generator (build-time only) | no |
| `data/master-data.json` | Single source of truth for the build | no (read by generator) |
| `src-static/` | Original Lovable-style data and templates - kept for reference | no |
| `build/build.js` | Node shim that invokes the Python generator | no |

## Build

```bash
npm run build
# OR
node build/build.js
# OR (run Python directly)
pip install jinja2
python3 scripts/import_data.py   # merge src-static/data/*.json -> data/master-data.json
python3 scripts/generate.py      # generate dist/
```

## Deploy on Cloudflare Pages

Two equally valid setups:

1. **Pre-built (simplest)** - `dist/` is committed, point Cloudflare at it:
   - Build command: (empty)
   - Output directory: `dist`

2. **Build on every push** - rebuild from sources:
   - Build command: `node build/build.js`
   - Output directory: `dist`
   - Cloudflare Pages includes Python 3 + pip in the build environment.

## Site map

- 1 home + 7 static (about, contact, pricing, FAQ, testimonials, free audit, sitemap, 404, privacy, terms)
- 28 service pages
- 10 PPC pages
- 231 industry pages
- 78 country hubs
- 245 city pages
- 165 free SEO tool pages with working vanilla-JS widgets
- 43 blog posts
- 29 resource download pages
- 22 languages (English at full depth, 21 stub clusters with localized chrome and hreflang clusters)
- sitemap.xml, sitemap.html, robots.txt, rss.xml, llms.txt, ai.txt, manifest.json

Every page has a unique title, meta description, JSON-LD schema (Organization, BreadcrumbList, Service, LocalBusiness, FAQPage, HowTo, BlogPosting, SoftwareApplication, etc.), breadcrumb nav, hreflang cluster across 22 languages, hidden CrawlerLinks block for crawl discovery, mega-menu navbar, and footer.

## Brand

- Founder: Shahab Abbasi (Founder and Lead SEO Strategist)
- HQ: Dubai, UAE
- Promise: ROI in 90 Days or We Work Free
- Email: hello@shahababbasi.com
- WhatsApp: +971 50 000 0000

## Editing content

Edit `src-static/data/*.json` (rich per-item content: services, industries, locations, tools, blog posts, etc.). On the next build, `scripts/import_data.py` overlays those edits onto the wide-coverage seed in `scripts/seed-master-data.json` and writes the merged result to `data/master-data.json`. Then `scripts/generate.py` renders the site.

To grow coverage (e.g. add a new city), just add a new entry to `src-static/data/locations.json` (or any other file) and rebuild.
