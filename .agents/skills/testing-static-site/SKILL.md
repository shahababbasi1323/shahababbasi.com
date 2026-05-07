---
name: testing-static-site
description: Build and end-to-end test the shahababbasi.com static site. Use when verifying any change to scripts/generate.py, scripts/import_data.py, src-static/data/*.json, templates/*, or anything else that changes the rendered HTML in dist/.
---

# Testing the static site

## What this app is

Pure HTML5 + Tailwind CDN + vanilla JS. No React, Vue, Astro, or any framework at runtime. The site is generated at build time from `data/master-data.json` via Python + Jinja2 (`scripts/generate.py`) and written to `dist/`. Cloudflare Pages serves `dist/` directly.

## Build pipeline

```
npm run build
  -> node build/build.js
     -> python3 scripts/import_data.py    # merges src-static/data/*.json overlays into data/master-data.json
     -> python3 scripts/generate.py       # renders 1,958 URLs into dist/ (22 languages)
```

Dependencies:
- Python 3 with `jinja2` (`build/build.js` auto-installs jinja2 via pip if missing)
- Node 18+ (only used to run the shim)

Rebuilding from scratch: `rm -rf dist && npm run build`. Expect `Wrote 1958 URLs across 22 languages.` and `Build complete. Output: dist/`.

## How to serve and test locally

```bash
cd dist && python3 -m http.server 8000 &
sleep 2
curl -sI http://localhost:8000/ | head -3        # expect HTTP/1.0 200 OK
```

Then browse:
- `http://localhost:8000/` - English home (dark navy + electric blue + neon green hero, 4 mega menus)
- `http://localhost:8000/services/technical-seo.html` - rich service page (TOC, pricing tiers, FAQ from data overlay)
- `http://localhost:8000/tools/word-counter.html` - typing into the textarea must update `Words` and `Characters` live (proves vanilla JS widget works)
- `http://localhost:8000/seo-services-new-york.html` - city landing
- `http://localhost:8000/industries/dentists.html` - industry landing
- `http://localhost:8000/ar/` - Arabic home, must render `<html lang="ar" dir="rtl">` with mirrored layout and Arabic nav labels
- `http://localhost:8000/sitemap.xml` - must contain ~1,958 `<url>` entries

Do NOT use the legacy `site/` output directory - we use `dist/` (Cloudflare Pages convention).

## Voice / content checks (master prompt rules)

These are shell-verifiable and should ALWAYS be zero on a passing build:

```bash
# Em-dashes (U+2014) and en-dashes (U+2013) - master prompt forbids both, hyphens only
grep -rEoh --include='*.html' '—' dist/ | wc -l   # expect 0
grep -rEoh --include='*.html' '–' dist/ | wc -l   # expect 0

# Emojis - master prompt forbids all emojis
python3 -c "
import re, pathlib
emoji_re = re.compile('[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\U00002700-\U000027BF]+')
total = sum(len(m) for p in pathlib.Path('dist').rglob('*.html') for m in emoji_re.findall(p.read_text(encoding='utf-8', errors='ignore')))
print(f'Emoji codepoints: {total}')
"
# expect 0

# Forbidden marketing phrases
for p in 'revolutionary' 'cutting-edge' "in today's fast-paced world" 'game-changer'; do
  echo "$p: $(grep -ril --include='*.html' "$p" dist/ | wc -l)"
done
# expect 0 for each
```

## Gotcha: em-dashes hide in source JSON as escaped \u2014

The richer overlay JSONs in `src-static/data/` (services.json, country-hubs.json, ppc-services.json, blog-posts.json) historically contained em-dashes both as raw `—` characters AND as JSON-escaped `\u2014` sequences. A naive `sed -i 's/—/-/g'` only catches the raw form. The escaped sequences survive into `data/master-data.json` and reappear in `dist/` after the next `npm run build`.

**Correct fix** (walks every string field of the JSON):

```python
import json, pathlib
for f in ['src-static/data/services.json', 'src-static/data/country-hubs.json',
          'src-static/data/ppc-services.json', 'src-static/data/blog-posts.json',
          'src-static/data/industries.json', 'src-static/data/tools.json',
          'src-static/data/resources.json', 'data/master-data.json']:
    p = pathlib.Path(f)
    if not p.exists(): continue
    data = json.loads(p.read_text(encoding='utf-8'))
    def walk(obj):
        if isinstance(obj, dict): return {k: walk(v) for k, v in obj.items()}
        if isinstance(obj, list): return [walk(v) for v in obj]
        if isinstance(obj, str):
            new = obj.replace('\u2014', ' - ').replace('\u2013', '-')
            while '  ' in new: new = new.replace('  ', ' ')
            return new
        return obj
    p.write_text(json.dumps(walk(data), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
```

Then `rm -rf dist && npm run build` and re-run the grep checks.

## Primary E2E test plan (Chrome + recording)

After `python3 -m http.server 8000` is up in `dist/`:

1. Maximize Chrome before recording (`sudo apt-get install -y wmctrl 2>/dev/null; wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz`).
2. Navigate to `http://localhost:8000/` - assert dark navy bg, hero H1 "Stop being invisible online. We put you on Page 1. Guaranteed.", floating WhatsApp FAB.
3. Hover the "Services" navbar item - assert a multi-column mega menu opens (NOT a single-column dropdown) with SEO and PPC categories plus a "See all services" link.
4. Visit `/services/technical-seo.html` - scroll to Pricing - assert tiers `$1,750 / $4,500 / $12,500`. Then scroll to FAQ - assert 4 service-specific questions (these come from the overlay data merge, not generic boilerplate).
5. Visit `/tools/word-counter.html` - type "this is a small test of seven words" into the textarea - assert `Words` displays `8` and `Characters` displays `35`. This proves the widget JS runs in the browser.
6. Visit `/seo-services-new-york.html` - assert H1 "SEO services in New York." and breadcrumb `Home / United States / New York`.
7. Visit `/industries/dentists.html` - assert H1 "SEO and digital marketing for dentists." and sidebar TOC.
8. Visit `/ar/` - assert `<html lang="ar" dir="rtl">`, mirrored layout, Arabic nav labels (الخدمات, الصناعات, المواقع...).
9. Visit `/sitemap.xml` - assert valid XML and ~1,958 `<url>` entries (`grep -c '<url>' dist/sitemap.xml`).
10. View-source on home (`view-source:http://localhost:8000/index.html`) - assert 23 `rel="alternate" hreflang` entries (22 langs + x-default) and 3 `application/ld+json` blocks (Organization, WebSite, BreadcrumbList).

Use `annotate_recording` to mark each test_start and assertion. Stop recording, attach to PR comment alongside per-test screenshots.

## Editing content

- Add/edit services: `src-static/data/services.json`
- Add/edit industries: `src-static/data/industries.json`
- Add/edit blog posts: `src-static/data/blog-posts.json`
- Add/edit tools: `src-static/data/tools.json`
- Add/edit countries: `src-static/data/country-hubs.json`
- Add new languages: extend `LANGUAGES` and `I18N` in `scripts/generate.py`
- Re-render: `npm run build`

The seed file `scripts/seed-master-data.json` has the wider skeleton (231 industries, 245 cities, 78 countries, 165 tools); `import_data.py` overlays the richer per-item content from `src-static/data/*.json` on top of it.

## Devin Secrets Needed

None for build/test - the site is fully static and self-contained. Future enhancements (Cloudflare Pages API push, contact form backend) may need credentials.
