"""Import / merge richer content from src-static/data/*.json (existing repo seed)
into our master-data.json. Their per-item content is richer (full FAQs,
process_steps, deliverables, etc.); our coverage is wider (74 countries vs 13,
232 cities vs 88, 164 industries vs 67, 22 languages vs 1).

Strategy: take our master-data.json as the canonical wide skeleton, then
overlay rich fields from theirs where slugs match. We KEEP our wide coverage
to satisfy the master prompt's 640+ URL requirement, while gaining their
richer per-item content where it exists.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DATA = ROOT / "src-static" / "data"
SEED = ROOT / "scripts" / "seed-master-data.json"
OUT = ROOT / "data" / "master-data.json"


def load(p: Path) -> object:
    return json.loads(p.read_text(encoding="utf-8"))


def by_slug(items: list[dict]) -> dict[str, dict]:
    return {it["slug"]: it for it in items}


def merge_service(base: dict, overlay: dict) -> dict:
    """Merge fields from existing src-static service into our schema."""
    base = dict(base)
    base["name"] = overlay.get("name", base["name"])
    base["metaTitle"] = overlay.get("meta_title")
    base["metaDescription"] = overlay.get("meta_description")
    base["heroTitle"] = overlay.get("hero_title")
    base["heroDescription"] = overlay.get("hero_description")
    base["whatIsTitle"] = overlay.get("what_is_title")
    base["whatIsDesc"] = overlay.get("what_is_desc")
    base["benefits"] = overlay.get("benefits", [])
    base["processSteps"] = overlay.get("process_steps", [])
    base["toolsUsed"] = overlay.get("tools_used", [])
    base["deliverables"] = overlay.get("deliverables", [])
    base["pricing"] = overlay.get("pricing")
    base["pricingNote"] = overlay.get("pricing_note")
    base["faqs"] = overlay.get("faqs", [])
    base["relatedServices"] = overlay.get("related_services", [])
    return base


def merge_industry(base: dict, overlay: dict) -> dict:
    base = dict(base)
    base["name"] = overlay.get("short_title", overlay.get("name", base["name"]))
    base["fullName"] = overlay.get("name", base["name"])
    base["metaTitle"] = overlay.get("meta_title")
    base["metaDescription"] = overlay.get("meta_description")
    base["heroTitle"] = overlay.get("hero_title")
    base["heroHighlight"] = overlay.get("hero_highlight")
    base["heroDescription"] = overlay.get("hero_description")
    base["challenges"] = overlay.get("challenges", [])
    base["approach"] = overlay.get("approach", [])
    base["keywords"] = overlay.get("keywords", [])
    base["caseStudy"] = overlay.get("case_study", [])
    base["faqs"] = overlay.get("faqs", [])
    base["relatedServices"] = overlay.get("related_services", [])
    base["relatedLocations"] = overlay.get("related_locations", [])
    return base


def merge_city(base: dict, overlay: dict) -> dict:
    base = dict(base)
    base["metaTitle"] = overlay.get("meta_title")
    base["metaDescription"] = overlay.get("meta_description")
    base["challenges"] = overlay.get("challenges", [])
    base["processSteps"] = overlay.get("process_steps", [])
    base["results"] = overlay.get("results", [])
    base["faqs"] = overlay.get("faqs", [])
    base["nearby"] = overlay.get("nearby", [])
    return base


def merge_country(base: dict, overlay: dict) -> dict:
    base = dict(base)
    base["metaTitle"] = overlay.get("meta_title")
    base["metaDescription"] = overlay.get("meta_description")
    base["heroHeading"] = overlay.get("hero_heading")
    base["heroDescription"] = overlay.get("hero_description")
    base["whyContent"] = overlay.get("why_content")
    base["countryCode"] = overlay.get("country_code", base.get("countryCode"))
    return base


def merge_tool(base: dict, overlay: dict) -> dict:
    base = dict(base)
    base["category"] = overlay.get("category", base.get("category"))
    base["description"] = overlay.get("description")
    base["metaDescription"] = overlay.get("meta_description")
    base["hasJs"] = overlay.get("has_js", False)
    base["toolType"] = overlay.get("tool_type")
    return base


def merge_blog(base: dict, overlay: dict) -> dict:
    base = dict(base)
    base["title"] = overlay.get("title", base.get("title"))
    base["metaTitle"] = overlay.get("meta_title")
    base["metaDescription"] = overlay.get("meta_description")
    base["excerpt"] = overlay.get("excerpt")
    base["author"] = overlay.get("author", "Shahab Abbasi")
    base["date"] = overlay.get("date", base.get("date"))
    base["readTime"] = overlay.get("read_time")
    base["category"] = overlay.get("category", base.get("category"))
    base["tags"] = overlay.get("tags", [])
    base["sections"] = overlay.get("sections", [])
    base["faqs"] = overlay.get("faqs", [])
    base["relatedSlugs"] = overlay.get("relatedSlugs", overlay.get("related_slugs", []))
    return base


def merge_ppc(base: dict, overlay: dict) -> dict:
    base = dict(base)
    base["name"] = overlay.get("name", base["name"])
    base["metaTitle"] = overlay.get("meta_title")
    base["metaDescription"] = overlay.get("meta_description")
    base["heroDescription"] = overlay.get("hero_description")
    base["features"] = overlay.get("features", [])
    base["processSteps"] = overlay.get("process_steps", [])
    base["faqs"] = overlay.get("faqs", [])
    return base


def merge_resource(base: dict, overlay: dict) -> dict:
    base = dict(base)
    base["title"] = overlay.get("title", base.get("title"))
    base["category"] = overlay.get("category")
    base["description"] = overlay.get("description")
    return base


def main():
    seed = load(SEED)

    services_overlay = by_slug(load(SRC_DATA / "services.json"))
    industries_overlay = by_slug(load(SRC_DATA / "industries.json"))
    locations_overlay = by_slug(load(SRC_DATA / "locations.json"))
    countries_overlay = by_slug(load(SRC_DATA / "country-hubs.json"))
    tools_overlay = by_slug(load(SRC_DATA / "tools.json"))
    blogs_overlay = by_slug(load(SRC_DATA / "blog-posts.json"))
    ppc_overlay = by_slug(load(SRC_DATA / "ppc-services.json"))
    resources_overlay = by_slug(load(SRC_DATA / "resources.json"))

    # Services: replace our list with theirs (richer content), but ensure all 19+ from seed are present
    merged_services = []
    seed_service_slugs = {s["slug"] for s in seed["services"]}
    overlay_only = [s for slug, s in services_overlay.items() if slug not in seed_service_slugs]
    for s in seed["services"]:
        if s["slug"] in services_overlay:
            merged_services.append(merge_service(s, services_overlay[s["slug"]]))
        else:
            merged_services.append(s)
    for s in overlay_only:
        # Synthesize a base entry from overlay
        base = {
            "slug": s["slug"],
            "name": s["name"],
            "primaryKeyword": s["name"],
            "lsiKeywords": [],
            "shortDescription": s.get("hero_description", s.get("meta_description", ""))[:200],
            "parentCategory": "SEO",
        }
        merged_services.append(merge_service(base, s))
    seed["services"] = merged_services

    # PPC: same logic
    merged_ppc = []
    seed_ppc_slugs = {s["slug"] for s in seed["ppcServices"]}
    overlay_only = [s for slug, s in ppc_overlay.items() if slug not in seed_ppc_slugs]
    for s in seed["ppcServices"]:
        if s["slug"] in ppc_overlay:
            merged_ppc.append(merge_ppc(s, ppc_overlay[s["slug"]]))
        else:
            merged_ppc.append(s)
    for s in overlay_only:
        base = {
            "slug": s["slug"],
            "name": s["name"],
            "primaryKeyword": s["name"],
            "lsiKeywords": [],
            "shortDescription": s.get("hero_description", "")[:200],
            "parentCategory": "PPC",
        }
        merged_ppc.append(merge_ppc(base, s))
    seed["ppcServices"] = merged_ppc

    # Industries: keep our wide list; overlay rich content where slugs match
    merged_industries = []
    seed_industry_slugs = {s["slug"] for s in seed["industries"]}
    overlay_only = [s for slug, s in industries_overlay.items() if slug not in seed_industry_slugs]
    for ind in seed["industries"]:
        if ind["slug"] in industries_overlay:
            merged_industries.append(merge_industry(ind, industries_overlay[ind["slug"]]))
        else:
            merged_industries.append(ind)
    # Add overlay-only industries to expand coverage
    for s in overlay_only:
        base = {
            "slug": s["slug"],
            "name": s.get("short_title", s["name"]),
            "category": s.get("category", "Other"),
            "primaryKeyword": s.get("short_title", s["name"]),
            "lsiKeywords": s.get("keywords", [])[:5],
        }
        merged_industries.append(merge_industry(base, s))
    seed["industries"] = merged_industries

    # Cities (locations): keep wide; overlay rich content
    merged_cities = []
    seed_city_slugs = {c["slug"] for c in seed["cities"]}
    overlay_only = [c for slug, c in locations_overlay.items() if slug not in seed_city_slugs]
    for c in seed["cities"]:
        if c["slug"] in locations_overlay:
            merged_cities.append(merge_city(c, locations_overlay[c["slug"]]))
        else:
            merged_cities.append(c)
    for c in overlay_only:
        base = {
            "slug": c["slug"],
            "name": c.get("city", c["slug"]),
            "country": c.get("country", "Worldwide"),
            "countryCode": c.get("country_code", ""),
            "region": "Global",
        }
        merged_cities.append(merge_city(base, c))
    seed["cities"] = merged_cities

    # Countries: keep wide; overlay rich content
    merged_countries = []
    seed_country_slugs = {c["slug"] for c in seed["countries"]}
    overlay_only = [c for slug, c in countries_overlay.items() if slug not in seed_country_slugs]
    for c in seed["countries"]:
        if c["slug"] in countries_overlay:
            merged_countries.append(merge_country(c, countries_overlay[c["slug"]]))
        else:
            merged_countries.append(c)
    for c in overlay_only:
        base = {
            "slug": c["slug"],
            "name": c.get("name", c["slug"]),
            "countryCode": c.get("country_code", ""),
            "region": "Global",
            "currency": "USD",
            "primaryKeyword": f"SEO Services {c.get('name', c['slug'])}",
            "lsiKeywords": [],
        }
        merged_countries.append(merge_country(base, c))
    seed["countries"] = merged_countries

    # Tools: keep wide; overlay description
    merged_tools = []
    seed_tool_slugs = {t["slug"] for t in seed["tools"]}
    overlay_only = [t for slug, t in tools_overlay.items() if slug not in seed_tool_slugs]
    for t in seed["tools"]:
        if t["slug"] in tools_overlay:
            merged_tools.append(merge_tool(t, tools_overlay[t["slug"]]))
        else:
            merged_tools.append(t)
    for t in overlay_only:
        base = {
            "slug": t["slug"],
            "name": t.get("name", t["slug"]),
            "category": t.get("category", "Other"),
            "primaryKeyword": t.get("name", t["slug"]),
            "lsiKeywords": [],
        }
        merged_tools.append(merge_tool(base, t))
    seed["tools"] = merged_tools

    # Blogs: keep wide; overlay rich content + sections
    merged_blogs = []
    seed_blog_slugs = {b["slug"] for b in seed["blogTopics"]}
    overlay_only = [b for slug, b in blogs_overlay.items() if slug not in seed_blog_slugs]
    for b in seed["blogTopics"]:
        if b["slug"] in blogs_overlay:
            merged_blogs.append(merge_blog(b, blogs_overlay[b["slug"]]))
        else:
            merged_blogs.append(b)
    for b in overlay_only:
        base = {
            "slug": b["slug"],
            "title": b.get("title", b["slug"]),
            "category": b.get("category", "SEO"),
            "primaryKeyword": b.get("title", ""),
            "lsiKeywords": [],
            "date": b.get("date", "2026-01-01"),
        }
        merged_blogs.append(merge_blog(base, b))
    seed["blogTopics"] = merged_blogs

    # Resources: keep wide; overlay description
    merged_resources = []
    seed_resource_slugs = {r["slug"] for r in seed["resources"]}
    overlay_only = [r for slug, r in resources_overlay.items() if slug not in seed_resource_slugs]
    for r in seed["resources"]:
        if r["slug"] in resources_overlay:
            merged_resources.append(merge_resource(r, resources_overlay[r["slug"]]))
        else:
            merged_resources.append(r)
    for r in overlay_only:
        base = {
            "slug": r["slug"],
            "title": r.get("title", r["slug"]),
            "category": r.get("category", "Resource"),
            "primaryKeyword": r.get("title", ""),
            "lsiKeywords": [],
        }
        merged_resources.append(merge_resource(base, r))
    seed["resources"] = merged_resources

    # ------------------------------------------------------------------
    # Boilerplate scrub on the master data file BEFORE persisting.
    # The seed file shipped tool entries whose ``shortDescription`` was
    # uniformly "Free <name> tool - run unlimited checks in your browser,
    # no signup required." That string then leaked into every place that
    # rendered ``s.shortDescription`` - the tool body intro, related-tools
    # cards on service detail pages, the JSON-LD SoftwareApplication
    # description, even other languages because the same data is used.
    #
    # Rewrite each tool's shortDescription to a unique action sentence
    # taken from ``description_engine.TOOL_ACTIONS`` (or derived from the
    # slug when no override exists). The fallback derivation matches the
    # composer in ``description_engine.for_tool`` so the data and the
    # composed meta description stay in sync.
    # ------------------------------------------------------------------
    try:
        import description_engine as _de  # noqa: E402 - local module
    except ImportError:
        # description_engine lives alongside this script - add scripts/ to
        # sys.path so it can be imported when running via the build shim.
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import description_engine as _de  # noqa: E402

    for t in seed["tools"]:
        slug = t.get("slug", "")
        action = _de.TOOL_ACTIONS.get(slug)
        if action:
            short = action
        else:
            # Fallback: derive a verb-led sentence from the slug suffix.
            name = (t.get("name") or _de._slug_to_friendly_tool_name(slug))
            lower = name.lower()
            if slug.endswith("-generator"):
                short = f"Generate {lower.replace(' generator','')} output from your inputs"
            elif slug.endswith(("-checker", "-tester", "-validator", "-inspector")):
                short = f"Check {lower.rsplit(' ', 1)[0]} against best-practice rules"
            elif slug.endswith("-calculator"):
                short = f"Calculate {lower.replace(' calculator','')} from your inputs"
            elif slug.endswith("-analyzer"):
                short = f"Analyze {lower.replace(' analyzer','')} across your inputs"
            elif slug.endswith("-optimizer"):
                short = f"Optimize {lower.replace(' optimizer','')} against documented best practice"
            elif slug.endswith("-tracker"):
                short = f"Track {lower.replace(' tracker','')} across runs and report deltas"
            elif slug.endswith("-finder"):
                short = f"Find {lower.replace(' finder','')} across the inputs you provide"
            elif slug.endswith("-builder"):
                short = f"Build {lower.replace(' builder','')} from inputs you control"
            elif slug.endswith("-counter"):
                short = f"Count {lower.replace(' counter','')} across any block of text"
            else:
                short = f"Free in-browser {lower} for SEOs, marketers, and growth teams"
        # Trailing period for grammar in card layouts.
        if not short.endswith((".", "!", "?")):
            short = short + "."
        t["shortDescription"] = short

    # Persist
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote merged master-data.json with:")
    print(f"  services: {len(seed['services'])}")
    print(f"  ppcServices: {len(seed['ppcServices'])}")
    print(f"  industries: {len(seed['industries'])}")
    print(f"  cities: {len(seed['cities'])}")
    print(f"  countries: {len(seed['countries'])}")
    print(f"  tools: {len(seed['tools'])}")
    print(f"  blogTopics: {len(seed['blogTopics'])}")
    print(f"  resources: {len(seed['resources'])}")
    print(f"  languages: {len(seed['languages'])}")


if __name__ == "__main__":
    main()
