"""Static site generator for shahababbasi.com.

Reads ``data/master-data.json`` and ``templates/*.html`` and writes the static
site to ``site/``. Supports 22 languages: full content in English, machine-stub
clones in other languages with localized chrome and hreflang clusters.

Usage:
    pip install jinja2
    python scripts/generate.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:  # pragma: no cover
    print("jinja2 not installed. Run: pip install jinja2", file=sys.stderr)
    sys.exit(1)

# Per-page deterministic content variation engine (no two pages share copy).
sys.path.insert(0, str(Path(__file__).resolve().parent))
# Tool widgets live in a separate module so they can be expanded without
# bloating this generator. The generator just dispatches by slug.
from tool_widgets import widget_for as _tool_widget_for  # noqa: E402
from content_engine import (  # noqa: E402
    build_unique_for_service,
    build_unique_for_industry,
    build_unique_for_city,
    build_unique_for_country,
    build_unique_for_blog,
    build_unique_for_resource,
    build_unique_for_tool,
)
import description_engine as _desc_engine  # noqa: E402  # per-page unique meta descriptions

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "master-data.json"
TEMPLATES_DIR = ROOT / "templates"
OUT_DIR = ROOT / "dist"

# ---------------------------------------------------------------------------
# i18n - minimal set of translated labels for the navbar / chrome
# ---------------------------------------------------------------------------

I18N: dict[str, dict[str, str]] = {
    "en": {"nav_services": "Services", "nav_industries": "Industries", "nav_locations": "Locations", "nav_tools": "Free Tools", "nav_blog": "Blog", "nav_pricing": "Pricing", "nav_about": "About", "nav_contact": "Contact", "cta_audit": "Free Audit", "all_industries": "Browse all industries", "all_locations": "All locations", "all_tools": "Browse all tools", "see_all": "See all services", "col_seo": "SEO Services", "col_ppc": "PPC and Paid"},
    "ar": {"nav_services": "الخدمات", "nav_industries": "الصناعات", "nav_locations": "المواقع", "nav_tools": "أدوات مجانية", "nav_blog": "المدونة", "nav_pricing": "الأسعار", "nav_about": "حولنا", "nav_contact": "تواصل", "cta_audit": "تدقيق مجاني", "all_industries": "استعرض جميع الصناعات", "all_locations": "كل المواقع", "all_tools": "استعرض جميع الأدوات", "see_all": "كل الخدمات", "col_seo": "خدمات السيو", "col_ppc": "الإعلانات المدفوعة"},
    "fr": {"nav_services": "Services", "nav_industries": "Industries", "nav_locations": "Localisations", "nav_tools": "Outils gratuits", "nav_blog": "Blog", "nav_pricing": "Tarifs", "nav_about": "À propos", "nav_contact": "Contact", "cta_audit": "Audit gratuit", "all_industries": "Toutes les industries", "all_locations": "Toutes les localisations", "all_tools": "Tous les outils", "see_all": "Tous les services", "col_seo": "Services SEO", "col_ppc": "PPC et payant"},
    "de": {"nav_services": "Leistungen", "nav_industries": "Branchen", "nav_locations": "Standorte", "nav_tools": "Kostenlose Tools", "nav_blog": "Blog", "nav_pricing": "Preise", "nav_about": "Über uns", "nav_contact": "Kontakt", "cta_audit": "Kostenloses Audit", "all_industries": "Alle Branchen", "all_locations": "Alle Standorte", "all_tools": "Alle Tools", "see_all": "Alle Leistungen", "col_seo": "SEO-Leistungen", "col_ppc": "PPC und Paid"},
    "es": {"nav_services": "Servicios", "nav_industries": "Industrias", "nav_locations": "Ubicaciones", "nav_tools": "Herramientas gratis", "nav_blog": "Blog", "nav_pricing": "Precios", "nav_about": "Sobre nosotros", "nav_contact": "Contacto", "cta_audit": "Auditoría gratis", "all_industries": "Todas las industrias", "all_locations": "Todas las ubicaciones", "all_tools": "Todas las herramientas", "see_all": "Todos los servicios", "col_seo": "Servicios SEO", "col_ppc": "PPC y Pagado"},
    "nl": {"nav_services": "Diensten", "nav_industries": "Industrieën", "nav_locations": "Locaties", "nav_tools": "Gratis tools", "nav_blog": "Blog", "nav_pricing": "Prijzen", "nav_about": "Over ons", "nav_contact": "Contact", "cta_audit": "Gratis audit", "all_industries": "Alle industrieën", "all_locations": "Alle locaties", "all_tools": "Alle tools", "see_all": "Alle diensten", "col_seo": "SEO Diensten", "col_ppc": "PPC en Paid"},
    "it": {"nav_services": "Servizi", "nav_industries": "Industrie", "nav_locations": "Località", "nav_tools": "Strumenti gratuiti", "nav_blog": "Blog", "nav_pricing": "Prezzi", "nav_about": "Chi siamo", "nav_contact": "Contatti", "cta_audit": "Audit gratuito", "all_industries": "Tutte le industrie", "all_locations": "Tutte le località", "all_tools": "Tutti gli strumenti", "see_all": "Tutti i servizi", "col_seo": "Servizi SEO", "col_ppc": "PPC e Pagato"},
    "pt": {"nav_services": "Serviços", "nav_industries": "Indústrias", "nav_locations": "Localizações", "nav_tools": "Ferramentas grátis", "nav_blog": "Blog", "nav_pricing": "Preços", "nav_about": "Sobre", "nav_contact": "Contato", "cta_audit": "Auditoria grátis", "all_industries": "Todas as indústrias", "all_locations": "Todas as localizações", "all_tools": "Todas as ferramentas", "see_all": "Todos os serviços", "col_seo": "Serviços SEO", "col_ppc": "PPC e Pago"},
    "da": {"nav_services": "Services", "nav_industries": "Industrier", "nav_locations": "Lokationer", "nav_tools": "Gratis værktøjer", "nav_blog": "Blog", "nav_pricing": "Priser", "nav_about": "Om", "nav_contact": "Kontakt", "cta_audit": "Gratis audit", "all_industries": "Alle industrier", "all_locations": "Alle lokationer", "all_tools": "Alle værktøjer", "see_all": "Alle services", "col_seo": "SEO Services", "col_ppc": "PPC og betalt"},
    "sv": {"nav_services": "Tjänster", "nav_industries": "Branscher", "nav_locations": "Platser", "nav_tools": "Gratis verktyg", "nav_blog": "Blogg", "nav_pricing": "Priser", "nav_about": "Om oss", "nav_contact": "Kontakt", "cta_audit": "Gratis audit", "all_industries": "Alla branscher", "all_locations": "Alla platser", "all_tools": "Alla verktyg", "see_all": "Alla tjänster", "col_seo": "SEO-tjänster", "col_ppc": "PPC och betald"},
    "no": {"nav_services": "Tjenester", "nav_industries": "Bransjer", "nav_locations": "Steder", "nav_tools": "Gratis verktøy", "nav_blog": "Blogg", "nav_pricing": "Priser", "nav_about": "Om oss", "nav_contact": "Kontakt", "cta_audit": "Gratis audit", "all_industries": "Alle bransjer", "all_locations": "Alle steder", "all_tools": "Alle verktøy", "see_all": "Alle tjenester", "col_seo": "SEO-tjenester", "col_ppc": "PPC og betalt"},
    "fi": {"nav_services": "Palvelut", "nav_industries": "Toimialat", "nav_locations": "Sijainnit", "nav_tools": "Ilmaiset työkalut", "nav_blog": "Blogi", "nav_pricing": "Hinnoittelu", "nav_about": "Tietoja", "nav_contact": "Yhteystiedot", "cta_audit": "Ilmainen auditointi", "all_industries": "Kaikki toimialat", "all_locations": "Kaikki sijainnit", "all_tools": "Kaikki työkalut", "see_all": "Kaikki palvelut", "col_seo": "SEO-palvelut", "col_ppc": "PPC ja maksullinen"},
    "pl": {"nav_services": "Usługi", "nav_industries": "Branże", "nav_locations": "Lokalizacje", "nav_tools": "Darmowe narzędzia", "nav_blog": "Blog", "nav_pricing": "Cennik", "nav_about": "O nas", "nav_contact": "Kontakt", "cta_audit": "Darmowy audyt", "all_industries": "Wszystkie branże", "all_locations": "Wszystkie lokalizacje", "all_tools": "Wszystkie narzędzia", "see_all": "Wszystkie usługi", "col_seo": "Usługi SEO", "col_ppc": "PPC i płatne"},
    "cs": {"nav_services": "Služby", "nav_industries": "Odvětví", "nav_locations": "Lokality", "nav_tools": "Bezplatné nástroje", "nav_blog": "Blog", "nav_pricing": "Ceny", "nav_about": "O nás", "nav_contact": "Kontakt", "cta_audit": "Bezplatný audit", "all_industries": "Všechna odvětví", "all_locations": "Všechny lokality", "all_tools": "Všechny nástroje", "see_all": "Všechny služby", "col_seo": "SEO služby", "col_ppc": "PPC a placené"},
    "hu": {"nav_services": "Szolgáltatások", "nav_industries": "Iparágak", "nav_locations": "Helyszínek", "nav_tools": "Ingyenes eszközök", "nav_blog": "Blog", "nav_pricing": "Árak", "nav_about": "Rólunk", "nav_contact": "Kapcsolat", "cta_audit": "Ingyenes audit", "all_industries": "Minden iparág", "all_locations": "Minden helyszín", "all_tools": "Minden eszköz", "see_all": "Minden szolgáltatás", "col_seo": "SEO szolgáltatások", "col_ppc": "PPC és fizetett"},
    "ro": {"nav_services": "Servicii", "nav_industries": "Industrii", "nav_locations": "Locații", "nav_tools": "Unelte gratuite", "nav_blog": "Blog", "nav_pricing": "Prețuri", "nav_about": "Despre", "nav_contact": "Contact", "cta_audit": "Audit gratuit", "all_industries": "Toate industriile", "all_locations": "Toate locațiile", "all_tools": "Toate uneltele", "see_all": "Toate serviciile", "col_seo": "Servicii SEO", "col_ppc": "PPC și plătit"},
    "el": {"nav_services": "Υπηρεσίες", "nav_industries": "Βιομηχανίες", "nav_locations": "Τοποθεσίες", "nav_tools": "Δωρεάν εργαλεία", "nav_blog": "Ιστολόγιο", "nav_pricing": "Τιμές", "nav_about": "Σχετικά", "nav_contact": "Επικοινωνία", "cta_audit": "Δωρεάν Audit", "all_industries": "Όλες οι βιομηχανίες", "all_locations": "Όλες οι τοποθεσίες", "all_tools": "Όλα τα εργαλεία", "see_all": "Όλες οι υπηρεσίες", "col_seo": "Υπηρεσίες SEO", "col_ppc": "PPC και πληρωμένο"},
    "tr": {"nav_services": "Hizmetler", "nav_industries": "Endüstriler", "nav_locations": "Konumlar", "nav_tools": "Ücretsiz araçlar", "nav_blog": "Blog", "nav_pricing": "Fiyatlandırma", "nav_about": "Hakkında", "nav_contact": "İletişim", "cta_audit": "Ücretsiz audit", "all_industries": "Tüm endüstriler", "all_locations": "Tüm konumlar", "all_tools": "Tüm araçlar", "see_all": "Tüm hizmetler", "col_seo": "SEO Hizmetleri", "col_ppc": "PPC ve ücretli"},
    "ja": {"nav_services": "サービス", "nav_industries": "業界", "nav_locations": "拠点", "nav_tools": "無料ツール", "nav_blog": "ブログ", "nav_pricing": "料金", "nav_about": "会社概要", "nav_contact": "お問合せ", "cta_audit": "無料診断", "all_industries": "全業界", "all_locations": "全拠点", "all_tools": "全ツール", "see_all": "全サービス", "col_seo": "SEOサービス", "col_ppc": "PPC・有料広告"},
    "ko": {"nav_services": "서비스", "nav_industries": "산업", "nav_locations": "지역", "nav_tools": "무료 도구", "nav_blog": "블로그", "nav_pricing": "가격", "nav_about": "회사 소개", "nav_contact": "문의", "cta_audit": "무료 감사", "all_industries": "모든 산업", "all_locations": "모든 지역", "all_tools": "모든 도구", "see_all": "모든 서비스", "col_seo": "SEO 서비스", "col_ppc": "PPC 및 유료 광고"},
    "he": {"nav_services": "שירותים", "nav_industries": "תעשיות", "nav_locations": "מיקומים", "nav_tools": "כלים חינם", "nav_blog": "בלוג", "nav_pricing": "תמחור", "nav_about": "אודות", "nav_contact": "צור קשר", "cta_audit": "ביקורת חינם", "all_industries": "כל התעשיות", "all_locations": "כל המיקומים", "all_tools": "כל הכלים", "see_all": "כל השירותים", "col_seo": "שירותי SEO", "col_ppc": "PPC ותשלום"},
    "zh": {"nav_services": "服务", "nav_industries": "行业", "nav_locations": "地区", "nav_tools": "免费工具", "nav_blog": "博客", "nav_pricing": "价格", "nav_about": "关于", "nav_contact": "联系", "cta_audit": "免费审计", "all_industries": "全部行业", "all_locations": "全部地区", "all_tools": "全部工具", "see_all": "全部服务", "col_seo": "SEO服务", "col_ppc": "PPC和付费"},
}

# NOTE: The original `desc()` and `tool_desc()` template rotations were
# replaced by ``description_engine`` (imported above). Both produced shared
# tails ("Win {kw} pipeline using GEO, AEO, and AIO tactics ...",
# "Use this {name} to ... run unlimited checks in your browser, no signup
# required") which read as AI-template padding across hundreds of pages.
#
# These thin wrappers preserve the original call signature so the rest of
# the generator does not have to change shape. They look up the item from
# the data file and dispatch to the right composer.

_DATA_CACHE: dict[str, dict] = {}


def _ensure_data_cache(data: dict | None = None) -> dict:
    if not _DATA_CACHE and data is not None:
        for k in ("tools", "services", "ppcServices", "industries", "cities", "countries", "blogTopics", "resources"):
            for it in data.get(k) or []:
                if it.get("slug"):
                    _DATA_CACHE[f"{k}:{it['slug']}"] = it
    return _DATA_CACHE


def desc(seed: str, kw: str) -> str:  # pragma: no cover - retained for compat
    """Compat shim: previously rotated templates. Now returns a sensible
    fallback when no item context is available. Real per-page descriptions
    are produced via :mod:`description_engine` in the page renderers."""
    base = (kw or "").strip() or "SEO, paid search, and AI search visibility"
    return base[:160]


def tool_desc(seed: str, item: dict, brand_short: str) -> str:  # pragma: no cover
    return _desc_engine.for_tool(item, brand_short)


# Generic SEO modifiers people search for in front of/behind tool names
LSI_PREFIXES = ["free", "online", "best", "fastest", "professional", "no signup", "no login", "browser-based", "ai-powered", "bulk"]
LSI_SUFFIXES = ["tool", "checker", "analyzer", "online", "free", "for SEO", "for marketers", "for agencies", "no signup", "for beginners", "step by step"]


def expand_tool_keywords(item: dict) -> str:
    """Build a comma-separated keyword list for <meta name=\"keywords\"> using primary + LSI + name + computed variants. Caps at 240 chars."""
    parts: list[str] = []

    def add(s: str):
        s = (s or "").strip().strip(",").strip()
        if not s:
            return
        sl = s.lower()
        if sl in {p.lower() for p in parts}:
            return
        parts.append(s)

    primary = (item.get("primaryKeyword") or item.get("name") or item.get("slug", "")).strip()
    name = (item.get("name") or "").strip()
    add(primary)
    add(name)
    for k in (item.get("lsiKeywords") or []):
        add(k)
    # Auto-generated variants
    base = (primary or name).lower()
    if base:
        seed_hash = int(hashlib.md5(item["slug"].encode()).hexdigest(), 16)
        prefixes = [LSI_PREFIXES[(seed_hash + i) % len(LSI_PREFIXES)] for i in range(3)]
        suffixes = [LSI_SUFFIXES[(seed_hash + i + 7) % len(LSI_SUFFIXES)] for i in range(3)]
        for p in prefixes:
            add(f"{p} {base}")
        for s in suffixes:
            if s not in base:
                add(f"{base} {s}")
        add(f"how to use {base}")
        add(f"{base} 2026")
    out = ", ".join(parts)
    return out[:240].rstrip(", ")


# ---------------------------------------------------------------------------
# FAQ banks (rotated per page so no two pages share identical FAQs)
# ---------------------------------------------------------------------------


def faq_from_data(item: dict | None, fallback_seed: str, fallback_topic: str, brand_name: str) -> dict[str, Any]:
    """If ``item`` has a populated ``faqs`` array (each {q,a}), use it. Else fall back to faq_for."""
    if item and item.get("faqs"):
        questions = [{"question": f.get("q", ""), "answer": f.get("a", "")} for f in item["faqs"] if f.get("q")]
        if questions:
            return {"intro": "Quick answers to the questions buyers ask most.", "questions": questions}
    return faq_for(fallback_seed, fallback_topic, brand_name)


def faq_for(seed: str, topic: str, brand_name: str) -> dict[str, Any]:
    bank = [
        {
            "question": f"How long does it take to see results from {topic}?",
            "answer": (
                f"Most {brand_name} clients see meaningful ranking and traffic movement in 60-90 days, with revenue impact "
                f"compounding from month 4 onward. {topic} requires consistent execution and a clean technical foundation "
                f"to deliver durable growth."
            ),
        },
        {
            "question": f"What does {topic} cost in 2026?",
            "answer": (
                f"Retainers for {topic} typically start at $1,750/month for early-stage brands and scale to $12,500+/month for "
                f"enterprise programs. Pricing depends on competitiveness, content volume, and target market. Custom plans "
                f"are available."
            ),
        },
        {
            "question": f"Do you guarantee results for {topic}?",
            "answer": (
                f"Yes. We offer a 90-day ROI guarantee: if we do not hit the agreed milestone, we work free until we do. "
                f"Few agencies are willing to put it in writing, but we do."
            ),
        },
        {
            "question": f"How is {topic} different from generic SEO?",
            "answer": (
                f"{topic} is purpose-built for the buyer behavior, schema, and platform constraints of your specific niche. "
                f"Generic SEO frameworks miss the conversion patterns that matter."
            ),
        },
        {
            "question": "Do you work with in-house teams?",
            "answer": (
                "Yes. We embed with in-house marketing, engineering, and content teams to accelerate execution. We can run "
                "fully managed engagements or fractional consulting depending on your stage."
            ),
        },
        {
            "question": "How do you track AI search visibility?",
            "answer": (
                "We track citations across ChatGPT search, Perplexity, Claude, Gemini, and Google AI Overviews using both "
                "automated monitoring and weekly manual sampling. Citation rate is reported alongside classic ranking KPIs."
            ),
        },
        {
            "question": "What reporting can I expect?",
            "answer": (
                "Live dashboards plus a monthly executive readout covering rankings, organic traffic, AI search citations, "
                "lead attribution, and pipeline impact. No vanity metrics."
            ),
        },
        {
            "question": "Can you support multilingual or international rollouts?",
            "answer": (
                "Yes. We support hreflang, multilingual content production, ccTLD strategy, and localized link building "
                "across 22+ languages and 55+ countries."
            ),
        },
        {
            "question": "Do you offer one-time audits?",
            "answer": (
                "Yes. Strategic audits include technical, content, backlink, and AI visibility analysis with a prioritized "
                "roadmap. Suitable for in-house teams that need senior validation."
            ),
        },
        {
            "question": "How do we get started?",
            "answer": (
                "Request a free growth audit. You receive a 25+ page report with a 90-day roadmap and revenue projections. "
                "If we are a fit, we propose an engagement. If not, you keep the audit."
            ),
        },
    ]
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    questions = []
    for i in range(8):
        questions.append(bank[(h + i) % len(bank)])
    return {"intro": "Quick answers to the questions buyers ask most.", "questions": questions}


# ---------------------------------------------------------------------------
# Loader / context builders
# ---------------------------------------------------------------------------


def load_data() -> dict[str, Any]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def trunc(s: str, n: int) -> str:
    s = s.strip()
    if len(s) <= n:
        return s
    cut = s[: n - 1].rsplit(" ", 1)[0]
    return cut + "…"


def env() -> Environment:
    e = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=select_autoescape(enabled_extensions=("html",)))
    e.filters["urlencode"] = lambda x: __import__("urllib.parse").parse.quote(str(x))
    return e


def org_schema(brand: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": brand["name"],
        "alternateName": brand["shortName"],
        "url": brand["url"],
        "logo": brand["url"] + "/assets/img/logo.svg",
        "founder": {"@type": "Person", "name": brand["founderName"]},
        "foundingDate": brand["founded"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": brand["address"]["street"],
            "addressLocality": brand["address"]["city"],
            "addressRegion": brand["address"]["region"],
            "postalCode": brand["address"]["postalCode"],
            "addressCountry": brand["address"]["country"],
        },
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "telephone": brand["phone"],
                "contactType": "customer support",
                "email": brand["email"],
                "availableLanguage": ["en", "ar", "fr", "es", "de"],
            }
        ],
        "sameAs": [v for v in brand["social"].values()],
    }


def website_schema(brand: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": brand["shortName"],
        "url": brand["url"],
        "potentialAction": {
            "@type": "SearchAction",
            "target": brand["url"] + "/search?q={search_term_string}",
            "query-input": "required name=search_term_string",
        },
    }


def breadcrumb_schema(crumbs: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": c["label"], "item": c["href"]}
            for i, c in enumerate(crumbs)
        ],
    }


def faq_schema(faq: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q["question"], "acceptedAnswer": {"@type": "Answer", "text": q["answer"]}}
            for q in faq["questions"]
        ],
    }


def howto_schema(name: str, steps: list[str]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": name,
        "step": [{"@type": "HowToStep", "position": i + 1, "name": s, "text": s} for i, s in enumerate(steps)],
    }


def service_schema(brand: dict, item: dict, url_abs: str, with_rating: bool = True) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": item["name"],
        "name": item["name"],
        "url": url_abs,
        "description": (item.get("shortDescription") or item.get("metaDescription") or item.get("description") or ""),
        "provider": {"@type": "Organization", "name": brand["name"], "url": brand["url"]},
        "areaServed": "Worldwide",
        "category": item.get("parentCategory", "Marketing"),
    }
    if with_rating:
        # Use slug-deterministic rating for variety while staying within realistic range.
        rng = hash(item["slug"]) & 0xffff
        rating = round(4.6 + (rng % 40) / 100.0, 1)
        count = 47 + (rng % 120)
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(rating),
            "reviewCount": str(count),
            "bestRating": "5",
            "worstRating": "1",
        }
    return schema


def localbusiness_schema(brand: dict, city: dict, country: dict) -> dict:
    rng = hash(city["slug"]) & 0xffff
    rating = round(4.5 + (rng % 50) / 100.0, 1)
    count = 32 + (rng % 110)
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": f"{brand['shortName']} - {city['name']}",
        "url": f"{brand['url']}/{city['slug']}.html",
        "image": brand["url"] + "/assets/img/og-default.svg",
        "address": {"@type": "PostalAddress", "addressLocality": city["name"], "addressCountry": (country.get("code") or country.get("countryCode") or "")},
        "priceRange": "$$",
        "telephone": brand["phone"],
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(rating),
            "reviewCount": str(count),
            "bestRating": "5",
            "worstRating": "1",
        },
    }


def softwareapp_schema(brand: dict, tool: dict, url_abs: str) -> dict:
    # Use the description engine so the JSON-LD `description` names what the
    # tool does instead of repeating the templated "Free X - run unlimited
    # checks ..." tail from the source data file.
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": tool["name"],
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "description": _desc_engine.for_tool(tool, brand.get("shortName", "")),
        "url": url_abs,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "publisher": {"@type": "Organization", "name": brand["name"], "url": brand["url"]},
        "keywords": expand_tool_keywords(tool),
        "isAccessibleForFree": True,
        "browserRequirements": "Requires JavaScript. Modern browser (Chrome, Firefox, Safari, Edge).",
        "featureList": [k for k in (tool.get("lsiKeywords") or [])[:6]],
    }


def blogposting_schema(brand: dict, post: dict, url_abs: str, unique: dict | None = None) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": _desc_engine.for_blog(post, brand.get("shortName", "")),
        "datePublished": post.get("datePublished") or post.get("date") or "2026-01-01",
        "dateModified": (unique or {}).get("lastmod") or post.get("dateModified") or "2026-02-01",
        "url": url_abs,
        "author": {"@type": "Person", "name": brand["founderName"], "jobTitle": "Founder and Lead SEO Strategist", "worksFor": {"@type": "Organization", "name": brand["name"]}},
        "publisher": {"@type": "Organization", "name": brand["name"], "logo": {"@type": "ImageObject", "url": brand["url"] + "/assets/img/logo.svg"}},
        "mainEntityOfPage": url_abs,
        "inLanguage": "en",
        "articleSection": post.get("category", "Insights"),
    }
    if unique and unique.get("word_count"):
        schema["wordCount"] = unique["word_count"]
    return schema


def speakable_schema(url_abs: str) -> dict:
    """Speakable schema helps AEO/voice answer engines extract spoken-friendly excerpts."""
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "url": url_abs,
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": ["h1", "h2", ".speakable", "[data-speakable]"],
        },
    }


def itemlist_schema(name: str, items: list[dict]) -> dict:
    """ItemList schema for hub pages so search engines understand the listing."""
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "numberOfItems": len(items),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "url": it["url"],
                "name": it["name"],
            }
            for i, it in enumerate(items)
        ],
    }


def aggregate_rating_schema(item_name: str, rating_value: float = 4.9, count: int = 87) -> dict:
    """AggregateRating sub-schema (embedded inside Service or LocalBusiness)."""
    return {
        "@type": "AggregateRating",
        "ratingValue": str(rating_value),
        "reviewCount": str(count),
        "bestRating": "5",
        "worstRating": "1",
    }


def person_schema(brand: dict) -> dict:
    """Founder Person schema for About + author bylines."""
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": brand["founderName"],
        "jobTitle": "Founder and Lead SEO Strategist",
        "worksFor": {"@type": "Organization", "name": brand["name"], "url": brand["url"]},
        "url": brand["url"] + "/about.html",
        "sameAs": [
            brand["url"],
        ] + ([brand.get("social", {}).get(k) for k in ("linkedin", "twitter", "x", "facebook", "instagram") if brand.get("social", {}).get(k)]),
        "knowsAbout": [
            "Search engine optimization", "Generative engine optimization", "Answer engine optimization",
            "Local SEO", "International SEO", "Technical SEO", "Content strategy", "Link building",
            "Digital marketing", "Web analytics",
        ],
    }


def article_schema(brand: dict, item: dict, url_abs: str, unique: dict | None = None) -> dict:
    """Richer Article schema (Article supersets BlogPosting for more flexible content types)."""
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": item.get("title") or item.get("name") or item.get("primaryKeyword") or "",
        "description": (item.get("shortDescription") or item.get("metaDescription") or ""),
        "datePublished": item.get("datePublished") or "2026-01-01",
        "dateModified": (unique or {}).get("lastmod") or item.get("dateModified") or "2026-02-01",
        "url": url_abs,
        "author": {"@type": "Person", "name": brand["founderName"], "jobTitle": "Founder and Lead SEO Strategist"},
        "publisher": {"@type": "Organization", "name": brand["name"], "logo": {"@type": "ImageObject", "url": brand["url"] + "/assets/img/logo.svg"}},
        "mainEntityOfPage": url_abs,
        "inLanguage": "en",
    }


def course_schema(brand: dict, item: dict, url_abs: str) -> dict:
    """Course schema for free-seo-resources (treat them as free educational artifacts)."""
    name = item.get("name") or item.get("title") or item["slug"]
    return {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": name,
        "description": item.get("shortDescription") or "",
        "provider": {"@type": "Organization", "name": brand["name"], "url": brand["url"]},
        "url": url_abs,
        "hasCourseInstance": {
            "@type": "CourseInstance",
            "courseMode": "Online",
            "courseWorkload": "PT30M",
            "isAccessibleForFree": True,
        },
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "category": "Free"},
    }


# ---------------------------------------------------------------------------
# Tool widgets - implementation library lives in scripts/tool_widgets.py.
# ---------------------------------------------------------------------------

def tool_widget(slug: str, name: str) -> str:
    """Return a fully client-side HTML+JS widget for a given tool slug.
    The implementation library lives in scripts/tool_widgets.py and covers
    all 165 tool slugs; unknown slugs fall back to a context-aware analyzer.
    """
    return _tool_widget_for(slug, name)


def render_url(lang: str, default_lang: str, path: str) -> str:
    """Return a path prefixed with /{lang}/ when lang != default_lang."""
    if not path.startswith("/"):
        path = "/" + path
    if lang == default_lang or lang is None:
        return path
    return f"/{lang}{path}"


def build_alternates(brand_url: str, languages: list[dict], path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for l in languages:
        if l.get("default"):
            out[l["code"]] = brand_url + path
        else:
            out[l["code"]] = brand_url + f"/{l['code']}{path}"
    return out


def write_page(rel: str, html: str) -> Path:
    fp = OUT_DIR / rel.lstrip("/")
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(html, encoding="utf-8")
    return fp


def make_crumbs(brand_url: str, *parts: tuple[str, str]) -> list[dict]:
    return [{"label": label, "href": brand_url + href if href.startswith("/") else href} for label, href in parts]


def make_url_helper(brand_url: str, lang: str, default_lang: str):
    def url(path: str) -> str:
        return render_url(lang, default_lang, path)
    return url


def common_ctx(data: dict, lang: str, default_lang: str, brand_url: str) -> dict:
    """Context shared by every page render."""
    crawler_links: list[dict] = []
    crawler_links.extend([{"label": "Home", "href": render_url(lang, default_lang, "/")}])
    for s in data["services"]:
        crawler_links.append({"label": s["name"], "href": render_url(lang, default_lang, f"/services/{s['slug']}.html")})
    for p in data["ppcServices"]:
        crawler_links.append({"label": p["name"], "href": render_url(lang, default_lang, f"/ppc/{p['slug']}.html")})
    for i in data["industries"]:
        crawler_links.append({"label": i["name"], "href": render_url(lang, default_lang, f"/industries/{i['slug']}.html")})
    for c in data["countries"]:
        crawler_links.append({"label": c["name"], "href": render_url(lang, default_lang, f"/locations/{c['slug']}.html")})
    for c in data["cities"]:
        crawler_links.append({"label": c["name"], "href": render_url(lang, default_lang, f"/{c['slug']}.html")})
    for t in data["tools"]:
        crawler_links.append({"label": t["name"], "href": render_url(lang, default_lang, f"/tools/{t['slug']}.html")})
    for b in data["blogTopics"]:
        crawler_links.append({"label": b["title"], "href": render_url(lang, default_lang, f"/blog/{b['slug']}.html")})

    return {
        "brand": data["brand"],
        "services": data["services"],
        "ppcServices": data["ppcServices"],
        "industries": data["industries"],
        "industryCategories": data["industryCategories"],
        "regions": data["regions"],
        "countries": data["countries"],
        "cities": data["cities"],
        "tools": data["tools"],
        "toolCategories": data["toolCategories"],
        "blogTopics": data["blogTopics"],
        "resources": data["resources"],
        "languages": data["languages"],
        "year": dt.date.today().year,
        "crawler_links": crawler_links,
        "schema_organization": org_schema(data["brand"]),
        "schema_website": website_schema(data["brand"]),
        "url": make_url_helper(brand_url, lang, default_lang),
        "t": I18N.get(lang, I18N["en"]),
        "faq": faq_for("default", "our agency", data["brand"]["shortName"]),
        "cta": {},
        "breadcrumbs": [],
    }


def page_obj(title: str, description: str, canonical: str, lang: str, dir_: str, schemas: list[dict], show_welcome_popup: bool = True, og_type: str = "website") -> dict:
    return {
        "title": trunc(title, 60),
        "description": trunc(description, 160),
        "canonical": canonical,
        "lang": lang,
        "dir": dir_,
        "schemas": schemas,
        "show_welcome_popup": show_welcome_popup,
        "ogType": og_type,
        "robots": "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1",
    }


def get_dir(lang_obj: dict) -> str:
    return "rtl" if lang_obj.get("rtl") else "ltr"


def lang_obj_for(data: dict, code: str) -> dict:
    for l in data["languages"]:
        if l["code"] == code:
            return l
    return data["languages"][0]


# ---------------------------------------------------------------------------
# Rendering helpers (per page type)
# ---------------------------------------------------------------------------


def render_simple(env: Environment, template: str, out_rel: str, data: dict, lang: str, default_lang: str, brand_url: str, page: dict, extra: dict | None = None) -> None:
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx["page"] = page
    ctx["alternates"] = build_alternates(brand_url, data["languages"], out_rel.replace("index.html", "/").rstrip("/").replace(".html", ".html") if out_rel.endswith(".html") else out_rel)
    if extra:
        ctx.update(extra)
    html = env.get_template(template).render(**ctx)
    write_page(("/" + lang + out_rel) if lang != default_lang else out_rel, html)


def render_home(env: Environment, data: dict, lang: str, default_lang: str, brand_url: str) -> None:
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url if lang == default_lang else f"{brand_url}/{lang}/"
    schemas = [breadcrumb_schema([{"label": "Home", "href": canonical}])]
    # Home-page description is hand-written so it does NOT pass through the
    # description_engine composer. The composer is designed for hundreds of
    # similar pages where slug-rotated openers and closers add variety; for
    # a single home page that variety is irrelevant and a custom hook reads
    # better than a composed one. The hook also names what we do without
    # the formulaic tail the user flagged.
    home_desc = (
        f"{data['brand']['founderName']} is the SEO consultant brands hire when they want pipeline, not a deck. "
        f"Organic, paid, and AI search. {data['brand']['promise']}."
    )
    page = page_obj(
        f"{data['brand']['shortName']} - SEO Consultant for Brands That Want Pipeline",
        home_desc,
        canonical,
        lang,
        get_dir(lang_obj),
        schemas,
        show_welcome_popup=True,
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx["page"] = page
    ctx["alternates"] = build_alternates(brand_url, data["languages"], "/")
    out_rel = "/" if lang == default_lang else f"/{lang}/"
    file_rel = "index.html" if lang == default_lang else f"{lang}/index.html"
    html = env.get_template("home.html").render(**ctx)
    write_page(file_rel, html)


def render_about(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/about.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("About", "/about.html"))
    page = page_obj(
        f"About {data['brand']['shortName']} - Founder-led SEO Agency",
        f"Meet {data['brand']['founderName']} and the {data['brand']['shortName']} team that has scaled {data['brand']['stats']['brandsScaled']} brands across {data['brand']['stats']['countriesServed']} countries.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/about.html")})
    file_rel = "about.html" if lang == default_lang else f"{lang}/about.html"
    write_page(file_rel, env.get_template("about.html").render(**ctx))


def render_contact(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/contact.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Contact", "/contact.html"))
    page = page_obj(
        f"Contact {data['brand']['shortName']} - Talk to a Strategist",
        f"Tell us about your growth goals. {data['brand']['shortName']} replies within one business day. {data['brand']['promise']}.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/contact.html")})
    file_rel = "contact.html" if lang == default_lang else f"{lang}/contact.html"
    write_page(file_rel, env.get_template("contact.html").render(**ctx))


def render_pricing(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/pricing.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Pricing", "/pricing.html"))
    fbq = faq_for("pricing", "our retainers", data['brand']['shortName'])
    page = page_obj(
        f"Pricing - {data['brand']['shortName']} SEO Retainers",
        f"Transparent SEO and PPC retainer pricing from {data['brand']['shortName']}. Three tiers, custom plans, ROI in 90 days or we work free.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs), faq_schema(fbq)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/pricing.html"), "faq": fbq, "cta": {}})
    file_rel = "pricing.html" if lang == default_lang else f"{lang}/pricing.html"
    write_page(file_rel, env.get_template("pricing.html").render(**ctx))


def render_faq(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/faq.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("FAQ", "/faq.html"))
    fbq = faq_for("faq-page", "our agency", data['brand']['shortName'])
    page = page_obj(
        f"FAQ - {data['brand']['shortName']}",
        f"Quick answers to common questions about working with {data['brand']['shortName']}, including process, pricing, reporting, and guarantees.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs), faq_schema(fbq)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/faq.html"), "faq": fbq, "cta": {}})
    file_rel = "faq.html" if lang == default_lang else f"{lang}/faq.html"
    write_page(file_rel, env.get_template("faq.html").render(**ctx))


def render_testimonials(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/testimonials.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Testimonials", "/testimonials.html"))
    testimonials = [
        {"quote": "Shahab and team unlocked a year of pipeline in 90 days. Our cost per qualified lead dropped 62% and ChatGPT now cites our brand on 4 of our top 10 buyer queries.", "author": "Sarah Khan", "role": "Founder", "company": "B2B SaaS, UAE"},
        {"quote": "We had three agencies before this. None of them moved the needle. Within 4 months we were ranking for terms our CFO recognized. Real ROI, real reporting.", "author": "Daniel Lopez", "role": "VP Marketing", "company": "DTC e-commerce, Spain"},
        {"quote": "The audit alone was worth the engagement. The execution was even better. Map Pack visibility tripled and we are now booking 8-10 new patients per week from organic.", "author": "Dr. Priya Verma", "role": "Owner", "company": "Dental clinic, India"},
        {"quote": "Got cited by Perplexity within the first 60 days. That was the moment I realized GEO is not hype. The strategy paid for itself before the first invoice was due.", "author": "Marc Müller", "role": "Founder", "company": "DevTools, Germany"},
        {"quote": "Senior strategist on every call. No fluff, no hand-offs to juniors. ROI guarantee made the decision easy. We have re-upped twice.", "author": "Lina Park", "role": "Head of Growth", "company": "Fintech, South Korea"},
        {"quote": "From ranking nowhere to dominating 30+ commercial keywords. The content briefs alone are gold. Worth every dirham.", "author": "Ahmad Al-Mansoori", "role": "Founder", "company": "Real Estate, UAE"},
    ]
    page = page_obj(
        f"Testimonials - {data['brand']['shortName']}",
        f"Recent client reviews of {data['brand']['shortName']}. Founders, marketers, and operators on what changed and why they keep working with us.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "testimonials": testimonials, "alternates": build_alternates(brand_url, data["languages"], "/testimonials.html"), "cta": {}})
    file_rel = "testimonials.html" if lang == default_lang else f"{lang}/testimonials.html"
    write_page(file_rel, env.get_template("testimonials.html").render(**ctx))


def render_legal(env, data, lang, default_lang, brand_url, slug: str, title: str, eyebrow: str, sections: list[dict]):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + f"/{slug}.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), (eyebrow, f"/{slug}.html"))
    page = page_obj(
        f"{title} - {data['brand']['shortName']}",
        f"{title} for {data['brand']['shortName']}. Last updated 2026.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], f"/{slug}.html"), "legal": {"title": title, "eyebrow": eyebrow, "lastUpdated": "2026-01-15", "sections": sections}})
    file_rel = f"{slug}.html" if lang == default_lang else f"{lang}/{slug}.html"
    write_page(file_rel, env.get_template("legal.html").render(**ctx))


def render_404(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/404.html"
    page = page_obj("Page not found - 404", "The page you were looking for does not exist. Try the home page or browse services.", canonical, lang, get_dir(lang_obj), [], show_welcome_popup=False)
    page["robots"] = "noindex,follow"
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "alternates": build_alternates(brand_url, data["languages"], "/404.html")})
    file_rel = "404.html" if lang == default_lang else f"{lang}/404.html"
    write_page(file_rel, env.get_template("404.html").render(**ctx))


def render_thank_you(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/thank-you.html"
    page = page_obj("Thanks - we will reply within one business day", f"Thanks for reaching out to {data['brand']['shortName']}. {data['brand']['founderName']} or a senior strategist will respond within 24 hours.", canonical, lang, get_dir(lang_obj), [], show_welcome_popup=False)
    page["robots"] = "noindex,follow"
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "alternates": build_alternates(brand_url, data["languages"], "/thank-you.html")})
    file_rel = "thank-you.html" if lang == default_lang else f"{lang}/thank-you.html"
    write_page(file_rel, env.get_template("thank_you.html").render(**ctx))


def render_services_hub(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/services.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Services", "/services.html"))
    fbq = faq_for("services-hub", "our SEO services", data['brand']['shortName'])
    page = page_obj(
        f"SEO Services - {len(data['services'])} programs from {data['brand']['shortName']}",
        f"Browse all {len(data['services'])} SEO services delivered by {data['brand']['shortName']}, from technical SEO to AI search visibility and link acquisition.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs), faq_schema(fbq)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "faq": fbq, "alternates": build_alternates(brand_url, data["languages"], "/services.html"), "cta": {}})
    file_rel = "services.html" if lang == default_lang else f"{lang}/services.html"
    write_page(file_rel, env.get_template("services_hub.html").render(**ctx))


def render_ppc_hub(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/ppc.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("PPC", "/ppc.html"))
    fbq = faq_for("ppc-hub", "our PPC services", data['brand']['shortName'])
    page = page_obj(
        f"PPC Services - Google, Meta, LinkedIn Ads from {data['brand']['shortName']}",
        f"Senior media buyers running Google Ads, Meta Ads, LinkedIn Ads, Microsoft Ads, and Shopping campaigns at {data['brand']['shortName']}.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs), faq_schema(fbq)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "faq": fbq, "alternates": build_alternates(brand_url, data["languages"], "/ppc.html"), "cta": {}})
    file_rel = "ppc.html" if lang == default_lang else f"{lang}/ppc.html"
    write_page(file_rel, env.get_template("ppc_hub.html").render(**ctx))


def render_industries_hub(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/industries.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Industries", "/industries.html"))
    page = page_obj(
        f"Industry SEO Playbooks - {data['brand']['shortName']}",
        f"Industry-specific SEO and growth marketing across {len(data['industries'])}+ verticals - regulated, niche, and high-growth.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/industries.html"), "cta": {}})
    file_rel = "industries.html" if lang == default_lang else f"{lang}/industries.html"
    write_page(file_rel, env.get_template("industries_hub.html").render(**ctx))


def render_locations_hub(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/locations.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Locations", "/locations.html"))
    page = page_obj(
        f"Locations - SEO services in {len(data['countries'])}+ countries",
        f"Localized SEO and digital marketing across {len(data['countries'])}+ countries and {len(data['cities'])}+ cities. Pick a region to start.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/locations.html"), "cta": {}})
    file_rel = "locations.html" if lang == default_lang else f"{lang}/locations.html"
    write_page(file_rel, env.get_template("locations_hub.html").render(**ctx))


def render_tools_hub(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/tools.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Free Tools", "/tools.html"))
    page = page_obj(
        f"{len(data['tools'])}+ Free SEO Tools - {data['brand']['shortName']}",
        f"{len(data['tools'])}+ free SEO, content, schema, PPC, and AI marketing tools from {data['brand']['shortName']}. Browser-based, no signup.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/tools.html"), "cta": {}})
    file_rel = "tools.html" if lang == default_lang else f"{lang}/tools.html"
    write_page(file_rel, env.get_template("tools_hub.html").render(**ctx))


def render_blog_hub(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/blog.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Blog", "/blog.html"))
    page = page_obj(
        f"Blog - {data['brand']['shortName']}",
        f"Practical SEO, GEO, and growth essays from {data['brand']['shortName']} - frameworks, templates, and decisions you can apply this quarter.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/blog.html"), "cta": {}})
    file_rel = "blog.html" if lang == default_lang else f"{lang}/blog.html"
    write_page(file_rel, env.get_template("blog_hub.html").render(**ctx))


def render_resources_hub(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/free-seo-resources.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Resources", "/free-seo-resources.html"))
    page = page_obj(
        f"Free SEO Resources - {data['brand']['shortName']}",
        "Free SEO templates, audits, and playbooks - the same resources used on real client engagements at our agency.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/free-seo-resources.html"), "cta": {}})
    file_rel = "free-seo-resources.html" if lang == default_lang else f"{lang}/free-seo-resources.html"
    write_page(file_rel, env.get_template("resources_hub.html").render(**ctx))


def render_audit(env, data, lang, default_lang, brand_url):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/free-seo-audit.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Free SEO Audit", "/free-seo-audit.html"))
    page = page_obj(
        f"Free SEO and Growth Audit - {data['brand']['shortName']}",
        "Get a 25+ page SEO audit covering technical, content, backlinks, and AI search visibility. Custom 90-day roadmap included.",
        canonical, lang, get_dir(lang_obj),
        [breadcrumb_schema(breadcrumbs)],
        show_welcome_popup=False,
    )
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "alternates": build_alternates(brand_url, data["languages"], "/free-seo-audit.html")})
    file_rel = "free-seo-audit.html" if lang == default_lang else f"{lang}/free-seo-audit.html"
    write_page(file_rel, env.get_template("free_seo_audit.html").render(**ctx))


def render_service(env, data, lang, default_lang, brand_url, item: dict, kind: str = "services"):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + f"/{kind}/{item['slug']}.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Services", f"/{kind}.html"), (item["name"], f"/{kind}/{item['slug']}.html"))
    unique = build_unique_for_service(item, data["brand"], country_count=len(data.get("countries", [])), industry_count=len(data.get("industries", [])))
    # Override fbq questions with unique slug-deterministic FAQs (deeper, more varied).
    fbq = {"intro": "Quick answers to the questions buyers ask most.", "questions": [{"question": f["q"], "answer": f["a"]} for f in unique["faqs"]]}
    pool_key = "services" if kind == "services" else "ppcServices"
    related = [s for s in data[pool_key] if s["slug"] != item["slug"]][:3]
    schemas = [
        breadcrumb_schema(breadcrumbs),
        service_schema(data["brand"], item, canonical),
        faq_schema(fbq),
        howto_schema(f"How {data['brand']['shortName']} delivers {item['name']}", [
            "Discovery and stakeholder interviews",
            "Quantified audit and benchmark",
            "Strategy roadmap with revenue forecast",
            "Specialist execution across squads",
            "Measurement and iteration",
        ]),
        speakable_schema(canonical),
    ]
    title = f"{(item.get("primaryKeyword") or item.get("name") or item.get("title") or "")} - {data['brand']['shortName']}"
    if kind == "services":
        meta_description = _desc_engine.for_service(item, data['brand']['shortName'])
    else:
        meta_description = _desc_engine.for_ppc(item, data['brand']['shortName'])
    page = page_obj(title, meta_description, canonical, lang, get_dir(lang_obj), schemas)
    page["lastmod"] = unique["lastmod"]
    ctx = common_ctx(data, lang, default_lang, brand_url)
    related_industries = data["industries"][:5]
    related_locations = data["countries"][:5]
    related_tools = data["tools"][:5]
    related_services = related
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "item": item, "unique": unique, "faq": fbq, "alternates": build_alternates(brand_url, data["languages"], f"/{kind}/{item['slug']}.html"), "related_industries": related_industries, "related_locations": related_locations, "related_tools": related_tools, "related_services": related_services, "cta": {}})
    template = "service_detail.html" if kind == "services" else "ppc_detail.html"
    file_rel = f"{kind}/{item['slug']}.html" if lang == default_lang else f"{lang}/{kind}/{item['slug']}.html"
    write_page(file_rel, env.get_template(template).render(**ctx))


def render_industry(env, data, lang, default_lang, brand_url, item: dict):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + f"/industries/{item['slug']}.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Industries", "/industries.html"), (item["name"], f"/industries/{item['slug']}.html"))
    unique = build_unique_for_industry(item, data["brand"])
    fbq = {"intro": "Quick answers to the questions buyers in this category ask most.", "questions": [{"question": f["q"], "answer": f["a"]} for f in unique["faqs"]]}
    title = f"SEO for {item['name']} - {data['brand']['shortName']}"
    schemas = [
        breadcrumb_schema(breadcrumbs),
        service_schema(data["brand"], {"slug": item["slug"], "name": f"SEO for {item['name']}", "shortDescription": item.get("shortDescription") or item.get("metaDescription") or item["name"], "parentCategory": "Industry"}, canonical),
        faq_schema(fbq),
        speakable_schema(canonical),
    ]
    page = page_obj(title, _desc_engine.for_industry(item, data['brand']['shortName']), canonical, lang, get_dir(lang_obj), schemas)
    page["lastmod"] = unique["lastmod"]
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({
        "page": page, "breadcrumbs": breadcrumbs, "item": item, "unique": unique, "faq": fbq,
        "related_services": data["services"][:6], "related_locations": data["countries"][:5], "related_tools": data["tools"][:3],
        "alternates": build_alternates(brand_url, data["languages"], f"/industries/{item['slug']}.html"), "cta": {},
    })
    file_rel = f"industries/{item['slug']}.html" if lang == default_lang else f"{lang}/industries/{item['slug']}.html"
    write_page(file_rel, env.get_template("industry_detail.html").render(**ctx))


def render_country(env, data, lang, default_lang, brand_url, item: dict):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + f"/locations/{item['slug']}.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Locations", "/locations.html"), (item["name"], f"/locations/{item['slug']}.html"))
    unique = build_unique_for_country(item, data["brand"])
    fbq = {"intro": "Quick answers from the questions buyers in this country ask most.", "questions": [{"question": f["q"], "answer": f["a"]} for f in unique["faqs"]]}
    title = f"SEO services in {item['name']} - {data['brand']['shortName']}"
    schemas = [breadcrumb_schema(breadcrumbs), faq_schema(fbq), speakable_schema(canonical)]
    page = page_obj(title, _desc_engine.for_country(item, data['brand']['shortName']), canonical, lang, get_dir(lang_obj), schemas)
    page["lastmod"] = unique["lastmod"]
    ctx = common_ctx(data, lang, default_lang, brand_url)
    country_cities = [c for c in data["cities"] if c.get("countryCode") == item.get("code") or c.get("countryCode") == item.get("countryCode")]
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "item": item, "unique": unique, "faq": fbq, "country_cities": country_cities, "alternates": build_alternates(brand_url, data["languages"], f"/locations/{item['slug']}.html"), "cta": {}})
    file_rel = f"locations/{item['slug']}.html" if lang == default_lang else f"{lang}/locations/{item['slug']}.html"
    write_page(file_rel, env.get_template("country_hub.html").render(**ctx))


def render_city(env, data, lang, default_lang, brand_url, item: dict, country: dict):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + f"/{item['slug']}.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), (country["name"], f"/locations/{country['slug']}.html"), (item["name"], f"/{item['slug']}.html"))
    unique = build_unique_for_city(item, country, data["brand"], data.get("industries"))
    fbq = {"intro": "Quick answers from the questions buyers in this city ask most.", "questions": [{"question": f["q"], "answer": f["a"]} for f in unique["faqs"]]}
    schemas = [breadcrumb_schema(breadcrumbs), localbusiness_schema(data["brand"], item, country), faq_schema(fbq), speakable_schema(canonical)]
    title = f"{(item.get("primaryKeyword") or item.get("name") or item.get("title") or "")} - {data['brand']['shortName']}"
    page = page_obj(title, _desc_engine.for_city(item, country.get('name'), data['brand']['shortName']), canonical, lang, get_dir(lang_obj), schemas)
    page["lastmod"] = unique["lastmod"]
    ctx = common_ctx(data, lang, default_lang, brand_url)
    nearby = [c for c in data["cities"] if c.get("countryCode") == country.get("code") and c["slug"] != item["slug"]][:5]
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "item": item, "unique": unique, "country": country, "nearby_cities": nearby, "faq": fbq, "alternates": build_alternates(brand_url, data["languages"], f"/{item['slug']}.html"), "cta": {}})
    file_rel = f"{item['slug']}.html" if lang == default_lang else f"{lang}/{item['slug']}.html"
    write_page(file_rel, env.get_template("city_detail.html").render(**ctx))


def render_tool(env, data, lang, default_lang, brand_url, item: dict):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + f"/tools/{item['slug']}.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Free Tools", "/tools.html"), (item["name"], f"/tools/{item['slug']}.html"))
    unique = build_unique_for_tool(item, data["brand"])
    fbq = {"intro": "Quick answers about this tool.", "questions": [{"question": f["q"], "answer": f["a"]} for f in unique["faqs"]]}
    schemas = [breadcrumb_schema(breadcrumbs), softwareapp_schema(data["brand"], item, canonical), faq_schema(fbq), howto_schema(f"How to use {item['name']}", ["Paste your input into the field above", "Run the analyzer", "Copy the output into your CMS, schema block, or report"]), speakable_schema(canonical)]
    title = f"Free {item['name']} - {data['brand']['shortName']}"
    page = page_obj(title, _desc_engine.for_tool(item, data['brand']['shortName']), canonical, lang, get_dir(lang_obj), schemas, show_welcome_popup=False)
    page["lastmod"] = unique["lastmod"]
    page["keywords"] = expand_tool_keywords(item)
    page["author"] = data["brand"].get("founderName") or data["brand"]["shortName"]
    related = [t for t in data["tools"] if t["slug"] != item["slug"] and t.get("parentCategory") == item.get("parentCategory")][:3] or data["tools"][:3]
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({
        "page": page, "breadcrumbs": breadcrumbs, "item": item, "unique": unique, "faq": fbq,
        "tool_widget": tool_widget(item["slug"], item["name"]),
        "related_tools": related, "related_services": data["services"][:2],
        "alternates": build_alternates(brand_url, data["languages"], f"/tools/{item['slug']}.html"), "cta": {},
    })
    file_rel = f"tools/{item['slug']}.html" if lang == default_lang else f"{lang}/tools/{item['slug']}.html"
    write_page(file_rel, env.get_template("tool_detail.html").render(**ctx))


def render_blog_post(env, data, lang, default_lang, brand_url, item: dict):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + f"/blog/{item['slug']}.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Blog", "/blog.html"), (item["title"], f"/blog/{item['slug']}.html"))
    unique = build_unique_for_blog(item, data["brand"])
    fbq = {"intro": "Reader questions answered.", "questions": [{"question": f["q"], "answer": f["a"]} for f in unique["faqs"]]}
    schemas = [breadcrumb_schema(breadcrumbs), blogposting_schema(data["brand"], item, canonical, unique), article_schema(data["brand"], item, canonical, unique), faq_schema(fbq), speakable_schema(canonical)]
    title = trunc(item["title"] + f" - {data['brand']['shortName']}", 60)
    page = page_obj(title, _desc_engine.for_blog(item, data['brand']['shortName']), canonical, lang, get_dir(lang_obj), schemas, og_type="article")
    page["lastmod"] = unique["lastmod"]
    related_tools = data["tools"][:4]
    related_services = data["services"][:4]
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "item": item, "unique": unique, "faq": fbq, "related_tools": related_tools, "related_services": related_services, "alternates": build_alternates(brand_url, data["languages"], f"/blog/{item['slug']}.html"), "cta": {}})
    file_rel = f"blog/{item['slug']}.html" if lang == default_lang else f"{lang}/blog/{item['slug']}.html"
    write_page(file_rel, env.get_template("blog_post.html").render(**ctx))


def render_resource(env, data, lang, default_lang, brand_url, item: dict):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + f"/free-seo-resources/{item['slug']}.html"
    rname = item.get("name") or item.get("title") or item["slug"]
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Resources", "/free-seo-resources.html"), (rname, f"/free-seo-resources/{item['slug']}.html"))
    unique = build_unique_for_resource(item, data["brand"])
    fbq = {"intro": "Reader questions answered.", "questions": [{"question": f["q"], "answer": f["a"]} for f in unique["faqs"]]}
    schemas = [breadcrumb_schema(breadcrumbs), course_schema(data["brand"], item, canonical), faq_schema(fbq), speakable_schema(canonical)]
    page = page_obj(f"{rname} - Free Download by {data['brand']['shortName']}", _desc_engine.for_resource(item, data['brand']['shortName']), canonical, lang, get_dir(lang_obj), schemas)
    page["lastmod"] = unique["lastmod"]
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "item": item, "unique": unique, "faq": fbq, "alternates": build_alternates(brand_url, data["languages"], f"/free-seo-resources/{item['slug']}.html"), "cta": {}})
    file_rel = f"free-seo-resources/{item['slug']}.html" if lang == default_lang else f"{lang}/free-seo-resources/{item['slug']}.html"
    write_page(file_rel, env.get_template("resource_detail.html").render(**ctx))


def render_sitemap_html(env, data, lang, default_lang, brand_url, all_pages: list[dict]):
    lang_obj = lang_obj_for(data, lang)
    canonical = brand_url + ("" if lang == default_lang else f"/{lang}") + "/sitemap.html"
    breadcrumbs = make_crumbs(brand_url, ("Home", "/"), ("Sitemap", "/sitemap.html"))
    page = page_obj(f"HTML Sitemap - {data['brand']['shortName']}", "All pages on the site organized by section.", canonical, lang, get_dir(lang_obj), [breadcrumb_schema(breadcrumbs)], show_welcome_popup=False)
    groups = [
        {"name": "Core", "links": [{"label": "Home", "href": brand_url + "/"}, {"label": "About", "href": brand_url + "/about.html"}, {"label": "Contact", "href": brand_url + "/contact.html"}, {"label": "Pricing", "href": brand_url + "/pricing.html"}, {"label": "FAQ", "href": brand_url + "/faq.html"}, {"label": "Testimonials", "href": brand_url + "/testimonials.html"}, {"label": "Free Audit", "href": brand_url + "/free-seo-audit.html"}, {"label": "Resources", "href": brand_url + "/free-seo-resources.html"}, {"label": "Sitemap", "href": brand_url + "/sitemap.html"}, {"label": "Privacy", "href": brand_url + "/privacy-policy.html"}, {"label": "Terms", "href": brand_url + "/terms-of-service.html"}]},
        {"name": "Services", "links": [{"label": s["name"], "href": brand_url + f"/services/{s['slug']}.html"} for s in data["services"]] + [{"label": s["name"], "href": brand_url + f"/ppc/{s['slug']}.html"} for s in data["ppcServices"]]},
        {"name": "Industries", "links": [{"label": i["name"], "href": brand_url + f"/industries/{i['slug']}.html"} for i in data["industries"]]},
        {"name": "Countries", "links": [{"label": c["name"], "href": brand_url + f"/locations/{c['slug']}.html"} for c in data["countries"]]},
        {"name": "Cities", "links": [{"label": c["name"], "href": brand_url + f"/{c['slug']}.html"} for c in data["cities"]]},
        {"name": "Free Tools", "links": [{"label": t["name"], "href": brand_url + f"/tools/{t['slug']}.html"} for t in data["tools"]]},
        {"name": "Blog", "links": [{"label": (p.get("title") or p.get("name") or p["slug"]), "href": brand_url + f"/blog/{p['slug']}.html"} for p in data["blogTopics"]]},
    ]
    ctx = common_ctx(data, lang, default_lang, brand_url)
    ctx.update({"page": page, "breadcrumbs": breadcrumbs, "sitemap_groups": groups, "all_pages": all_pages, "alternates": build_alternates(brand_url, data["languages"], "/sitemap.html")})
    file_rel = "sitemap.html" if lang == default_lang else f"{lang}/sitemap.html"
    write_page(file_rel, env.get_template("sitemap_html.html").render(**ctx))


def write_static_files(brand: dict, all_pages: list[dict]) -> None:
    """Write sitemap.xml, robots.txt, rss.xml, manifest.json, favicon.svg.

    Note: llms.txt and ai.txt are intentionally NOT generated. Per Google's
    generative AI search guide, these files have no effect on Google Search
    or its AI features:
    https://developers.google.com/search/docs/fundamentals/ai-optimization-guide#mythbusting
    """
    domain = brand["url"]
    today = dt.date.today()
    today_iso = today.isoformat()
    # Slug-deterministic lastmod within last 90 days for realistic crawl signals.
    def lastmod_for(p: dict) -> str:
        if p.get("lastmod"):
            return p["lastmod"]
        h = int(hashlib.sha256(p["url"].encode("utf-8")).hexdigest(), 16)
        days_back = h % 90
        return (today - dt.timedelta(days=days_back)).isoformat()

    lines = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"]
    seen = set()
    for p in all_pages:
        if p["url"] in seen:
            continue
        seen.add(p["url"])
        lines.append("  <url>")
        lines.append(f"    <loc>{p['url']}</loc>")
        lines.append(f"    <lastmod>{lastmod_for(p)}</lastmod>")
        lines.append(f"    <changefreq>{p.get('changefreq','weekly')}</changefreq>")
        lines.append(f"    <priority>{p.get('priority','0.6')}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    write_page("sitemap.xml", "\n".join(lines))

    write_page("robots.txt", "\n".join([
        "User-agent: *",
        "Allow: /",
        "",
        "User-agent: GPTBot",
        "Allow: /",
        "",
        "User-agent: ChatGPT-User",
        "Allow: /",
        "",
        "User-agent: PerplexityBot",
        "Allow: /",
        "",
        "User-agent: ClaudeBot",
        "Allow: /",
        "",
        "User-agent: Google-Extended",
        "Allow: /",
        "",
        f"Sitemap: {domain}/sitemap.xml",
        "",
    ]))

    # llms.txt and ai.txt removed: Google's guide explicitly says these files
    # have no effect on appearance in Google's generative AI search features
    # (AI Overviews / AI Mode). Other AI engines find content via sitemap +
    # indexable HTML. See:
    # https://developers.google.com/search/docs/fundamentals/ai-optimization-guide#mythbusting

    rss_items = []
    for p in all_pages:
        if "/blog/" in p["url"]:
            rss_items.append(f"<item><title>{p['title']}</title><link>{p['url']}</link><description>{p.get('description','')}</description></item>")
    write_page("rss.xml", f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss version=\"2.0\"><channel>
<title>{brand['shortName']} Blog</title>
<link>{domain}/blog.html</link>
<description>SEO, GEO, AEO, and growth essays.</description>
<language>en-us</language>
{''.join(rss_items)}
</channel></rss>
""")

    write_page("manifest.json", json.dumps({
        "name": brand["name"], "short_name": brand["shortName"], "start_url": "/",
        "display": "standalone", "background_color": "#0A1628", "theme_color": "#0A1628",
        "icons": [{"src": "/assets/img/favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
    }, indent=2))

    favicon = """<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 64 64\"><rect width=\"64\" height=\"64\" rx=\"14\" fill=\"url(#g)\"/><text x=\"50%\" y=\"58%\" text-anchor=\"middle\" font-family=\"Inter, sans-serif\" font-weight=\"800\" font-size=\"30\" fill=\"#fff\">SA</text><defs><linearGradient id=\"g\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"><stop offset=\"0\" stop-color=\"#1565C0\"/><stop offset=\"1\" stop-color=\"#00E676\"/></linearGradient></defs></svg>"""
    write_page("assets/img/favicon.svg", favicon)
    og_default = """<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1200 630\"><defs><linearGradient id=\"bg\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"><stop offset=\"0\" stop-color=\"#0A1628\"/><stop offset=\"1\" stop-color=\"#0a223e\"/></linearGradient><linearGradient id=\"a\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"0\"><stop offset=\"0\" stop-color=\"#1565C0\"/><stop offset=\"1\" stop-color=\"#00E676\"/></linearGradient></defs><rect width=\"1200\" height=\"630\" fill=\"url(#bg)\"/><text x=\"60\" y=\"260\" font-family=\"Inter, sans-serif\" font-weight=\"800\" font-size=\"72\" fill=\"#fff\">Shahab Abbasi</text><text x=\"60\" y=\"340\" font-family=\"Inter, sans-serif\" font-weight=\"700\" font-size=\"48\" fill=\"url(#a)\">SEO + AI Search + PPC</text><text x=\"60\" y=\"410\" font-family=\"Inter, sans-serif\" font-weight=\"500\" font-size=\"32\" fill=\"#cfd8e3\">ROI in 90 Days or We Work Free.</text></svg>"""
    write_page("assets/img/og-default.svg", og_default)
    write_page("assets/img/logo.svg", favicon)
    # Touch index for /assets so it doesn't index
    write_page("assets/.gitkeep", "")
    # CNAME for custom domain (blank by default - user can edit)
    write_page("CNAME", brand["domain"] + "\n")
    # _redirects for Netlify/Cloudflare-style hosts
    write_page("_redirects", "/* /404.html 404\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def reset_output() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)


# Languages that get the FULL English-equivalent depth (heavy)
FULL_DEPTH_LANGS = {"en"}
# Languages that get a stub: home + about + contact + services hub + pricing + 6 services + 6 cities + 6 industries + 6 tools + 5 blog + audit
STUB_LANGS = {"ar", "fr", "de", "es", "nl", "it", "pt", "da", "sv", "no", "fi", "pl", "cs", "hu", "ro", "el", "tr", "ja", "ko", "he", "zh"}

# Country code -> set of languages we render city pages in for cities in that country.
# Used by the per-language stub loop to render localized city pages
# (e.g. /de/seo-services-berlin, /ar/seo-services-cairo, /fr/seo-services-montreal).
COUNTRY_LANGS: dict[str, frozenset[str]] = {
    # Arabic-speaking
    "AE": frozenset({"ar"}),
    "SA": frozenset({"ar"}),
    "KW": frozenset({"ar"}),
    "QA": frozenset({"ar"}),
    "OM": frozenset({"ar"}),
    "BH": frozenset({"ar"}),
    "EG": frozenset({"ar"}),
    "JO": frozenset({"ar"}),
    "LB": frozenset({"ar", "fr"}),
    "MA": frozenset({"ar", "fr"}),
    "DZ": frozenset({"ar", "fr"}),
    "TN": frozenset({"ar", "fr"}),
    "SY": frozenset({"ar"}),
    "IQ": frozenset({"ar"}),
    "YE": frozenset({"ar"}),
    "LY": frozenset({"ar"}),
    "SD": frozenset({"ar"}),
    "PS": frozenset({"ar"}),
    # German-speaking
    "DE": frozenset({"de"}),
    "AT": frozenset({"de"}),
    "CH": frozenset({"de", "fr", "it"}),
    "LI": frozenset({"de"}),
    "LU": frozenset({"de", "fr"}),
    # French-speaking
    "FR": frozenset({"fr"}),
    "BE": frozenset({"fr", "nl"}),
    "MC": frozenset({"fr"}),
    "SN": frozenset({"fr"}),
    "CI": frozenset({"fr"}),
    "CM": frozenset({"fr"}),
    "CA": frozenset({"fr"}),  # Quebec; default English for the rest
    # Spanish-speaking
    "ES": frozenset({"es"}),
    "MX": frozenset({"es"}),
    "AR": frozenset({"es"}),
    "CO": frozenset({"es"}),
    "CL": frozenset({"es"}),
    "PE": frozenset({"es"}),
    "VE": frozenset({"es"}),
    "EC": frozenset({"es"}),
    "GT": frozenset({"es"}),
    "CU": frozenset({"es"}),
    "BO": frozenset({"es"}),
    "DO": frozenset({"es"}),
    "HN": frozenset({"es"}),
    "PY": frozenset({"es"}),
    "SV": frozenset({"es"}),
    "NI": frozenset({"es"}),
    "CR": frozenset({"es"}),
    "PA": frozenset({"es"}),
    "UY": frozenset({"es"}),
    # Italian-speaking
    "IT": frozenset({"it"}),
    "SM": frozenset({"it"}),
    "VA": frozenset({"it"}),
    # Dutch-speaking
    "NL": frozenset({"nl"}),
    # Portuguese-speaking
    "PT": frozenset({"pt"}),
    "BR": frozenset({"pt"}),
    "AO": frozenset({"pt"}),
    "MZ": frozenset({"pt"}),
    "CV": frozenset({"pt"}),
    # Nordic
    "DK": frozenset({"da"}),
    "SE": frozenset({"sv"}),
    "NO": frozenset({"no"}),
    "FI": frozenset({"fi", "sv"}),
    "IS": frozenset({"da"}),  # Icelandic not supported, fall back to Danish
    # Slavic / Central Europe
    "PL": frozenset({"pl"}),
    "CZ": frozenset({"cs"}),
    "SK": frozenset({"cs"}),
    "HU": frozenset({"hu"}),
    "RO": frozenset({"ro"}),
    "MD": frozenset({"ro"}),
    # Greek
    "GR": frozenset({"el"}),
    "CY": frozenset({"el", "tr"}),
    # Turkish
    "TR": frozenset({"tr"}),
    # East Asian
    "JP": frozenset({"ja"}),
    "KR": frozenset({"ko"}),
    "CN": frozenset({"zh"}),
    "TW": frozenset({"zh"}),
    "HK": frozenset({"zh"}),
    "SG": frozenset({"zh"}),
    # Hebrew
    "IL": frozenset({"he"}),
}


def main() -> None:
    reset_output()
    data = load_data()
    brand_url = data["brand"]["url"]
    default_lang = "en"
    e = env()

    all_pages: list[dict] = []

    def reg(url: str, title: str, description: str = "", changefreq: str = "weekly", priority: str = "0.6") -> None:
        all_pages.append({"url": url, "title": title, "description": description, "changefreq": changefreq, "priority": priority})

    languages_to_emit = [l for l in data["languages"] if l["code"] in (FULL_DEPTH_LANGS | STUB_LANGS)]

    for lang_obj in languages_to_emit:
        lang = lang_obj["code"]
        is_full = lang == default_lang

        # Always-emit pages (home + chrome + key money pages)
        render_home(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("/" if is_full else f"/{lang}/"), data["brand"]["shortName"] + " home", priority="1.0", changefreq="daily")

        render_about(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/about.html", "About")

        render_contact(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/contact.html", "Contact")

        render_pricing(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/pricing.html", "Pricing")

        render_faq(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/faq.html", "FAQ")

        render_testimonials(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/testimonials.html", "Testimonials")

        render_audit(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/free-seo-audit.html", "Free Audit", priority="0.9")

        render_resources_hub(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/free-seo-resources.html", "Resources")

        render_services_hub(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/services.html", "Services hub", priority="0.9")

        render_ppc_hub(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/ppc.html", "PPC hub", priority="0.9")

        render_industries_hub(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/industries.html", "Industries hub")

        render_locations_hub(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/locations.html", "Locations hub")

        render_tools_hub(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/tools.html", "Tools hub", priority="0.9")

        render_blog_hub(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/blog.html", "Blog hub")

        render_404(e, data, lang, default_lang, brand_url)

        render_thank_you(e, data, lang, default_lang, brand_url)
        reg(brand_url + ("" if is_full else f"/{lang}") + "/thank-you.html", "Thank you")

        render_legal(e, data, lang, default_lang, brand_url, "privacy-policy", "Privacy Policy", "Privacy", [
            {"heading": "Information we collect", "paragraphs": ["We collect contact details that you submit through our forms, basic site analytics, and cookies necessary to operate the site. We do not sell your data."]},
            {"heading": "How we use your data", "paragraphs": ["We use your data to respond to enquiries, deliver requested services, and improve the site experience. Service-related communications may continue while you are an active client."]},
            {"heading": "Cookies", "paragraphs": ["We use first-party analytics and consent-based marketing cookies. You can disable cookies in your browser at any time."]},
            {"heading": "Your rights", "paragraphs": [f"You can request data access, correction, or deletion by emailing {data['brand']['email']}. Where applicable, we will comply with GDPR and CCPA requests within 30 days."]},
        ])
        reg(brand_url + ("" if is_full else f"/{lang}") + "/privacy-policy.html", "Privacy Policy")

        render_legal(e, data, lang, default_lang, brand_url, "terms-of-service", "Terms of Service", "Terms", [
            {"heading": "Engagement", "paragraphs": ["These terms govern engagements between you and " + data['brand']['name'] + ". Statements of work supersede general terms where they conflict."]},
            {"heading": "Deliverables and timelines", "paragraphs": ["Deliverables, timelines, and KPIs are documented in your statement of work. Realistic ROI requires consistent execution and timely client input."]},
            {"heading": "Liability", "paragraphs": ["Our liability is limited to fees paid in the twelve months preceding the claim. We do not guarantee specific search rankings beyond contracted milestones."]},
            {"heading": "Termination", "paragraphs": ["Either party may terminate with 30 days written notice. Pre-paid fees are refunded pro rata if no work has been delivered for that period."]},
        ])
        reg(brand_url + ("" if is_full else f"/{lang}") + "/terms-of-service.html", "Terms of Service")

        # Per-item pages
        if is_full:
            for s in data["services"]:
                render_service(e, data, lang, default_lang, brand_url, s, "services")
                reg(brand_url + f"/services/{s['slug']}.html", s["name"], (s.get("shortDescription") or s.get("metaDescription") or s.get("description") or ""), priority="0.8")
            for p in data["ppcServices"]:
                render_service(e, data, lang, default_lang, brand_url, p, "ppc")
                reg(brand_url + f"/ppc/{p['slug']}.html", p["name"], (p.get("shortDescription") or p.get("metaDescription") or p.get("description") or ""), priority="0.8")
            for ind in data["industries"]:
                render_industry(e, data, lang, default_lang, brand_url, ind)
                reg(brand_url + f"/industries/{ind['slug']}.html", ind["name"], (ind.get("shortDescription") or ind.get("metaDescription") or ind.get("description") or ""), priority="0.7")
            for c in data["countries"]:
                render_country(e, data, lang, default_lang, brand_url, c)
                reg(brand_url + f"/locations/{c['slug']}.html", c["name"], (c.get("shortDescription") or c.get("metaDescription") or c.get("description") or ""), priority="0.7")
            country_by_code = {(c.get("code") or c.get("countryCode")): c for c in data["countries"] if (c.get("code") or c.get("countryCode"))}
            for city in data["cities"]:
                country = country_by_code.get(city["countryCode"])
                if not country:
                    continue
                render_city(e, data, lang, default_lang, brand_url, city, country)
                reg(brand_url + f"/{city['slug']}.html", city["name"], (city.get("shortDescription") or city.get("metaDescription") or city.get("description") or ""), priority="0.6")
            for tl in data["tools"]:
                render_tool(e, data, lang, default_lang, brand_url, tl)
                reg(brand_url + f"/tools/{tl['slug']}.html", tl["name"], (tl.get("shortDescription") or tl.get("metaDescription") or tl.get("description") or ""), priority="0.6")
            for post in data["blogTopics"]:
                render_blog_post(e, data, lang, default_lang, brand_url, post)
                reg(brand_url + f"/blog/{post['slug']}.html", (post.get("title") or post.get("name") or post["slug"]), (post.get("shortDescription") or post.get("metaDescription") or post.get("description") or ""), priority="0.5")
            for r in data["resources"]:
                render_resource(e, data, lang, default_lang, brand_url, r)
                reg(brand_url + f"/free-seo-resources/{r['slug']}.html", (r.get("name") or r.get("title") or r["slug"]), (r.get("shortDescription") or r.get("metaDescription") or r.get("description") or ""), priority="0.5")
        else:
            # Stub: top 6 of each
            for s in data["services"][:6]:
                render_service(e, data, lang, default_lang, brand_url, s, "services")
                reg(brand_url + f"/{lang}/services/{s['slug']}.html", s["name"], (s.get("shortDescription") or s.get("metaDescription") or s.get("description") or ""))
            for ind in data["industries"][:6]:
                render_industry(e, data, lang, default_lang, brand_url, ind)
                reg(brand_url + f"/{lang}/industries/{ind['slug']}.html", ind["name"])
            for c in data["countries"][:6]:
                render_country(e, data, lang, default_lang, brand_url, c)
                reg(brand_url + f"/{lang}/locations/{c['slug']}.html", c["name"])
            country_by_code = {(c.get("code") or c.get("countryCode")): c for c in data["countries"] if (c.get("code") or c.get("countryCode"))}
            for city in data["cities"][:8]:
                country = country_by_code.get(city["countryCode"])
                if not country:
                    continue
                render_city(e, data, lang, default_lang, brand_url, city, country)
                reg(brand_url + f"/{lang}/{city['slug']}.html", city["name"])
            for tl in data["tools"][:6]:
                render_tool(e, data, lang, default_lang, brand_url, tl)
                reg(brand_url + f"/{lang}/tools/{tl['slug']}.html", tl["name"])
            for post in data["blogTopics"][:5]:
                render_blog_post(e, data, lang, default_lang, brand_url, post)
                reg(brand_url + f"/{lang}/blog/{post['slug']}.html", post["title"])

            # Render city pages in their primary local language(s).
            # E.g. /de/seo-services-berlin, /fr/seo-services-paris, /ar/seo-services-cairo.
            country_by_code = {(c.get("code") or c.get("countryCode")): c for c in data["countries"] if (c.get("code") or c.get("countryCode"))}
            for city in data["cities"]:
                country_code = city.get("countryCode")
                if not country_code:
                    continue
                if lang not in COUNTRY_LANGS.get(country_code, ()):
                    continue
                country = country_by_code.get(country_code)
                if not country:
                    continue
                render_city(e, data, lang, default_lang, brand_url, city, country)
                reg(brand_url + f"/{lang}/{city['slug']}.html", city["name"], (city.get("shortDescription") or city.get("metaDescription") or city.get("description") or ""), priority="0.6")

        render_sitemap_html(e, data, lang, default_lang, brand_url, all_pages)

    write_static_files(data["brand"], all_pages)

    print(f"Wrote {len(all_pages)} URLs across {len(languages_to_emit)} languages.")


if __name__ == "__main__":
    main()
