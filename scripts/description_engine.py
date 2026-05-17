"""Per-page unique meta description composer.

Replaces the original ``desc()`` / ``tool_desc()`` template rotation in
``generate.py``. The original code produced descriptions like:

    "Win {kw} pipeline using GEO, AEO, and AIO tactics that get cited inside ChatGPT and Google AI Overviews."
    "Use this {Tool} to free {tool} - run unlimited checks in your browser, no signup required."

Those reused identical tails across 600+ pages, which reads as AI-template
padding to humans and as duplicate-content boilerplate to crawlers.

This module composes a description per item using:

* item-specific facts (slug, name, parentCategory, primaryKeyword, country, ...)
* slug-hashed pool selections so two pages from the same category get different
  opener / closer combinations
* a per-tool action map so each tool's description names what the tool does
  rather than reusing a "Free X - run unlimited checks" tail

Composed descriptions target 125 to 165 characters for Latin scripts. The
``trunc()`` at 160 in ``page_obj()`` is still the upper guard; this module
aims to stay under that without truncation.
"""
from __future__ import annotations

import hashlib
import re
from typing import Optional

DESC_MIN = 110
DESC_MAX = 160


def _seed(slug: str, salt: str = "") -> int:
    h = hashlib.md5((salt + ":" + slug).encode("utf-8")).hexdigest()
    return int(h, 16)


def _pick(slug: str, salt: str, pool: list[str]) -> str:
    return pool[_seed(slug, salt) % len(pool)]


def _clean(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    s = s.replace(" ,", ",").replace(" .", ".").replace("..", ".")
    return s


def _strip_trailing(s: str) -> str:
    return s.rstrip(" .,;:!?")


def _compose(parts: list[str], max_len: int = DESC_MAX) -> str:
    """Compose a description from ordered sentence fragments.

    The FIRST part is treated as the lead and is always emitted (truncated
    cleanly at the last sentence boundary that fits in ``max_len`` if it is
    too long). Subsequent parts are appended only if they fit within the
    remaining budget; if they do not fit, they are skipped (NOT substituted
    for the lead - that was the original bug that produced descriptions
    consisting only of a closer like "Quarterly re-benchmark, no surprise
    upsell." with the actual subject of the page missing).
    """
    parts = [_clean(p) for p in parts if _clean(p)]
    if not parts:
        return ""
    lead = _strip_trailing(parts[0]) + "."
    if len(lead) > max_len:
        # Truncate the lead at the last word boundary that fits within
        # max_len - 1 (to leave room for the final period).
        cut = lead.rfind(" ", 0, max_len - 1)
        if cut < 0:
            cut = max_len - 1
        lead = _strip_trailing(lead[:cut]) + "."
    out = lead
    for p in parts[1:]:
        candidate = out + " " + _strip_trailing(p) + "."
        if len(candidate) > max_len:
            continue
        out = candidate
    return out


# ---------------------------------------------------------------------------
# Tool action map - what each tool actually does, in one short verb-led clause.
# ---------------------------------------------------------------------------
# Hand-written so every tool description names a real action, not a generic
# "run unlimited checks" template. Keys are tool slugs. Each value should:
#   - start with a verb in imperative form
#   - stay under ~75 chars
#   - not include the brand or boilerplate
TOOL_ACTIONS: dict[str, str] = {
    "keyword-density-analyzer": "Count keyword frequency and density percentages across any text or URL",
    "keyword-difficulty-estimator": "Estimate ranking difficulty for any keyword using domain authority signals",
    "long-tail-keyword-generator": "Generate long-tail keyword variations from a seed term using question and modifier patterns",
    "search-intent-classifier": "Classify any keyword as informational, navigational, commercial, or transactional",
    "lsi-keyword-generator": "Generate latent-semantic and related-term keyword suggestions for any topic",
    "paa-question-extractor": "Extract People Also Ask questions and structure them for FAQ schema",
    "keyword-cluster-builder": "Group keywords into topical clusters that map to URL targets and content briefs",
    "robotstxt-tester": "Test whether a robots.txt rule allows or blocks any URL for any user-agent",
    "xml-sitemap-generator": "Generate an XML sitemap from a URL list with lastmod and priority controls",
    "hreflang-tag-generator": "Generate hreflang tags for multilingual sites with x-default and region fallbacks",
    "canonical-tag-checker": "Audit a page's canonical tag and flag conflicts with redirects or alternates",
    "http-header-inspector": "Inspect HTTP response headers, status codes, and security headers for any URL",
    "redirect-chain-checker": "Trace redirect chains, count hops, and flag loops or excessive 301 stacks",
    "mobile-friendly-tester": "Test mobile friendliness with viewport, tap-target, and font-size checks",
    "core-web-vitals-checker": "Check LCP, INP, and CLS against the Core Web Vitals pass thresholds",
    "crawl-budget-estimator": "Estimate crawl budget consumption based on URL count, depth, and parameter sprawl",
    "word-counter": "Count words, characters, sentences, and reading time in any block of text",
    "readability-score-calculator": "Calculate Flesch, Flesch-Kincaid, Gunning Fog, and SMOG readability scores",
    "content-gap-analyzer": "Compare two URL sets and surface topic and keyword gaps between them",
    "meta-tag-generator": "Compose title, description, robots, and canonical tags from a single form",
    "title-tag-optimizer": "Score a title tag for length, keyword position, and SERP truncation",
    "meta-description-generator": "Compose a meta description with character budget, CTA, and keyword targeting",
    "opengraph-tag-generator": "Generate Open Graph tags for shareable cards on Facebook, LinkedIn, and Slack",
    "twitter-card-generator": "Generate Twitter Card tags for summary, summary_large_image, and player cards",
    "serp-snippet-preview": "Preview how a title and description will render in Google's search snippet",
    "slug-generator": "Convert any title into a clean, lowercase, hyphenated URL slug",
    "title-case-converter": "Convert text to AP, APA, Chicago, MLA, or sentence-case title formatting",
    "plagiarism-checker": "Highlight potential duplicate phrases between two blocks of text",
    "backlink-quality-checker": "Score a backlink against authority, relevance, anchor, and toxicity signals",
    "domain-authority-estimator": "Estimate domain authority from referring-domain count and link velocity inputs",
    "anchor-text-distribution": "Analyze the distribution of branded, exact, partial, and generic anchors in a profile",
    "broken-link-finder": "Crawl a page and flag broken internal and outbound links with status codes",
    "linkable-asset-idea-generator": "Generate linkable-asset ideas for any niche using proven format patterns",
    "nap-consistency-checker": "Compare Name, Address, and Phone across citations and flag inconsistencies",
    "citation-audit-tool": "Audit local citations for completeness, accuracy, and high-authority directory coverage",
    "google-business-profile-audit": "Audit a Google Business Profile for completeness, categories, and review signals",
    "local-schema-generator": "Generate LocalBusiness schema with address, hours, geo, and review data",
    "map-pack-position-tracker": "Track map-pack ranking position for a business across multiple geo-targeted queries",
    "geo-modifier-generator": "Generate city, neighborhood, and metro geo modifiers for local keyword variations",
    "ai-overview-visibility-checker": "Check whether a URL is cited inside Google AI Overviews for a target query",
    "chatgpt-citation-tracker": "Track when a URL or brand is cited by ChatGPT for tracked prompt sets",
    "perplexity-citation-tracker": "Track Perplexity citations for a domain across tracked prompts and answer panels",
    "ai-content-detector": "Detect AI-generated patterns in text using perplexity and burstiness signals",
    "ai-title-generator": "Generate title tag candidates from a topic using SERP-aware patterns",
    "ai-faq-generator": "Generate FAQ questions and answers from a topic, primed for FAQ schema",
    "ai-meta-description-generator": "Generate meta description variants within a character budget for any topic",
    "ai-schema-generator": "Generate JSON-LD schema for any page type using your inputs and best-practice fields",
    "faq-schema-generator": "Generate FAQ schema JSON-LD from question and answer pairs",
    "howto-schema-generator": "Generate HowTo schema with step images, total time, and supply inputs",
    "article-schema-generator": "Generate Article schema with headline, author, datePublished, and image fields",
    "product-schema-generator": "Generate Product schema with offers, aggregateRating, and review nodes",
    "localbusiness-schema-generator": "Generate LocalBusiness schema with hours, geo, and review snippet",
    "breadcrumb-schema-generator": "Generate BreadcrumbList schema from a URL path with itemListElement nodes",
    "videoobject-schema-generator": "Generate VideoObject schema with thumbnailUrl, duration, and uploadDate fields",
    "review-schema-generator": "Generate Review and AggregateRating schema for testimonial and rating widgets",
    "event-schema-generator": "Generate Event schema with location, startDate, and offers blocks for rich snippets",
    "cpc-calculator": "Calculate cost-per-click from spend and clicks, with currency and date-range inputs",
    "roas-calculator": "Calculate return on ad spend from revenue and ad spend with break-even analysis",
    "ctr-calculator": "Calculate click-through rate from impressions and clicks across campaigns",
    "quality-score-estimator": "Estimate Google Ads Quality Score from expected CTR, ad relevance, and landing-page signals",
    "ad-copy-generator": "Generate Google Ads, Meta Ads, and LinkedIn Ads copy variants from a single brief",
    "utm-builder": "Build UTM-tagged campaign URLs with source, medium, campaign, term, and content parameters",
    "negative-keyword-generator": "Generate negative keyword lists from a seed term using common irrelevant modifiers",
    "index-coverage-checker": "Check whether a URL is indexed in Google using site: operator probes",
    "bulk-indexing-checker": "Check indexed status for many URLs at once using site: operator probes per URL",
    "crawl-stats-estimator": "Estimate crawl request volume, response size, and average response time per URL",
    "url-inspector": "Run URL Inspection style checks on a single URL: canonical, robots, indexability, schema",
    "cro-heuristic-checklist": "Score a landing page against 30 CRO heuristics across copy, layout, proof, and CTA",
    "above-the-fold-tester": "Test what renders above the fold at desktop, tablet, and mobile breakpoints",
    "cta-strength-analyzer": "Score a CTA against 8 conversion criteria: clarity, urgency, proof, friction, value",
    "form-field-counter": "Count form fields, required fields, and field types and benchmark against conversion data",
    "page-speed-to-conversion-estimator": "Estimate revenue impact from LCP and INP improvements on conversion rate",
    "monthly-seo-report-generator": "Generate a monthly SEO report from GA4 and Search Console exports with executive summary",
    "kpi-tracker": "Track SEO and PPC KPIs across weeks with target lines and variance flags",
    "rank-tracking-snapshot": "Capture a one-time rank snapshot for a keyword list across desktop and mobile",
    "traffic-forecaster": "Forecast organic traffic from keyword volume, CTR curve, and ranking probability inputs",
    "pipeline-attribution-calculator": "Calculate pipeline attribution across SEO, paid, and direct touchpoints",
    "hashtag-generator": "Generate hashtag sets for Instagram, TikTok, LinkedIn, and Twitter from a topic",
    "linkedin-post-optimizer": "Score a LinkedIn post for hook, length, line breaks, and engagement triggers",
    "twitter-bio-optimizer": "Score a Twitter bio against character budget, keyword presence, and CTA strength",
    "instagram-caption-generator": "Generate Instagram caption variants with hook, value, and CTA in one tap",
    "youtube-title-optimizer": "Score a YouTube title for CTR signals: numbers, brackets, emotion, and keyword position",
    "youtube-tag-generator": "Generate YouTube tag sets from a video topic using broad and long-tail patterns",
    "pinterest-pin-title-generator": "Generate Pinterest pin title variants for vertical pins and idea pins",
    "tiktok-hook-generator": "Generate TikTok hook lines for the first three seconds across proven hook patterns",
    "social-share-image-sizer": "Resize and crop a single image into all required social share aspect ratios",
    "url-shortener": "Shorten a long URL into a clean, trackable redirect with optional UTM preservation",
    "html-encoder-decoder": "Encode and decode HTML entities, URL components, and Base64 strings in one place",
    "htaccess-generator": "Generate .htaccess rules for redirects, force-https, gzip, and cache headers",
    "schema-validator": "Validate JSON-LD schema against Google's structured-data requirements per type",
    "robotstxt-generator": "Generate a robots.txt file with allow, disallow, sitemap, and host directives",
    "bulk-index-checker": "Open Google site: queries for many URLs in batched tabs to check indexed status",
    "bulk-keyword-checker": "Open Google branded SERP queries for many keywords at once with location targeting",
    # ------------------------------------------------------------------
    # Tools added through import_data.py merging (extended catalog)
    # ------------------------------------------------------------------
    "character-counter": "Count characters, words, lines, and reading time across any block of text",
    "keyword-density-checker": "Check keyword frequency and density across a page or pasted text",
    "readability-checker": "Score text on Flesch, Flesch-Kincaid, Gunning Fog, and grade-level readability",
    "plagiarism-sentence-checker": "Highlight near-duplicate sentences between two blocks of pasted text",
    "lorem-ipsum-generator": "Generate Lorem Ipsum filler text in paragraphs, sentences, or words for layout mock-ups",
    "text-case-converter": "Convert text between upper, lower, sentence, title, and camel case in one click",
    "article-rewriter-helper": "Rewrite a paragraph at the click of a button, with synonym and tone suggestions",
    "headline-analyzer": "Score headline strength on emotion, power words, length, and CTR signals",
    "grammar-checker": "Highlight common grammar, punctuation, and spelling slips across pasted text",
    "google-serp-preview": "Preview a page's title and description as they render in Google search results",
    "bulk-title-checker": "Audit title tags for length, keyword position, and SERP truncation across many URLs",
    "meta-description-checker": "Audit meta descriptions for length, keyword presence, and CTA strength across pages",
    "heading-analyzer": "Audit H1-H6 structure on a page for hierarchy, length, and keyword coverage",
    "image-alt-text-generator": "Generate alt text candidates for an image based on its filename and context",
    "canonical-tag-generator": "Generate canonical link tags with self-canonical and cross-domain variants",
    "open-graph-preview": "Preview how a URL renders as an Open Graph card on Facebook, LinkedIn, and Slack",
    "google-index-checker": "Open a Google site: query for a URL to confirm whether the page is indexed",
    "serp-checker": "Open a Google search for any keyword with location and device parameters",
    "robots-txt-generator": "Generate a robots.txt file with allow, disallow, sitemap, and crawl-delay directives",
    "sitemap-generator": "Generate an XML sitemap from a list of URLs with lastmod and priority hints",
    "htaccess-redirect-generator": "Generate .htaccess 301 redirect rules from old-URL to new-URL pairs",
    "schema-generator": "Generate JSON-LD schema for the page type you select using the inputs you provide",
    "json-ld-validator": "Validate JSON-LD schema against Google's structured-data requirements",
    "url-encoder-decoder": "Encode and decode URL components, query strings, and special characters",
    "http-status-checker": "Check HTTP status codes, redirects, and response headers for any URL",
    "page-size-checker": "Estimate total page size, request count, and largest resource for any URL",
    "core-web-vitals-guide": "Reference guide to LCP, INP, and CLS thresholds, root causes, and proven fixes",
    "page-speed-analyzer": "Run a quick PageSpeed analysis for a URL and surface the top wins",
    "xml-to-url-converter": "Extract every URL from an XML sitemap into a clean copy-paste list",
    "keyword-suggestion-tool": "Generate seed and long-tail keyword suggestions for any topic",
    "question-generator": "Generate question-format keyword variants from a seed topic for FAQ targeting",
    "competitor-keyword-gap-planner": "Plan keyword gap targets between you and a competitor URL list",
    "keyword-grouper": "Group a keyword list into topical clusters that map to URL targets",
    "linkedin-post-formatter": "Format a LinkedIn post with line breaks, emoji caps, and hook-line spacing",
    "linkedin-headline-generator": "Generate LinkedIn headline variants from a role, value-prop, and target audience",
    "linkedin-summary-generator": "Generate LinkedIn About section copy from a role, wins, and current focus",
    "twitter-thread-formatter": "Format a long block of text into a numbered Twitter thread within character limits",
    "social-media-image-size-guide": "Reference guide to image dimensions and aspect ratios across every social platform",
    "instagram-bio-generator": "Generate Instagram bio variants from a niche, value-prop, and CTA",
    "social-post-scheduler-planner": "Plan a weekly social post cadence across channels with topic and CTA prompts",
    "local-citation-finder": "Find local citation opportunities for a business by category and city",
    "review-response-generator": "Generate professional review responses for positive, neutral, and negative reviews",
    "local-keyword-generator": "Generate local keyword variations from a seed term and city, neighborhood, or ZIP",
    "gbp-keyword-checker": "Check whether a Google Business Profile is matching for target local keywords",
    "ai-search-prompt-tester": "Test ChatGPT, Perplexity, and Gemini prompts for citation visibility on a topic",
    "ai-content-optimizer": "Score a draft against AI Overview citation signals: entities, citations, structure",
    "brand-mention-tracker-guide": "Reference guide for tracking brand mentions across web, social, and AI engines",
    "anchor-text-analyzer": "Analyze the anchor text distribution of links pointing at a URL or domain",
    "guest-post-pitch-generator": "Generate guest-post pitch email variants from your topic and target publication",
    "broken-link-outreach-template": "Outreach email templates for broken-link building with proven response rates",
    "backlink-quality-checklist": "Score a candidate backlink against authority, relevance, anchor, and toxicity criteria",
    "disavow-file-generator": "Generate a Google Search Console disavow file from a toxic-link URL list",
    "product-description-optimizer": "Optimize a product description for organic search, schema, and conversion signals",
    "ecommerce-schema-generator": "Generate Product, Offer, and AggregateRating schema for an ecommerce page",
    "category-page-optimizer": "Audit and optimize an ecommerce category page for ranking and faceted-nav signals",
    "seo-roi-calculator": "Calculate SEO ROI from traffic, conversion rate, AOV, and retainer cost inputs",
    "cpc-savings-calculator": "Estimate CPC savings from shifting paid traffic to organic ranked URLs",
    "domain-age-checker": "Check the WHOIS registration age of any domain and its renewal date",
    "website-cost-estimator": "Estimate website build cost from pages, complexity, and integration count",
    "cta-generator": "Generate CTA copy variants from a value-prop, audience, and conversion goal",
    "ab-test-duration-calculator": "Calculate A/B test duration from traffic, conversion rate, and minimum detectable effect",
    "color-contrast-checker": "Check WCAG color contrast ratios for foreground and background pairs",
    "page-speed-checklist": "Reference checklist of page speed wins across CSS, JS, images, and fonts",
    "email-subject-line-tester": "Score email subject lines for length, power words, and spam triggers",
    "cold-email-generator": "Generate cold-email variants from a prospect role, value-prop, and CTA",
    "google-ads-budget-calculator": "Calculate a Google Ads daily budget from monthly cap, CPC, and target click volume",
    "ppc-campaign-audit-checklist": "Audit a Google Ads or Meta Ads campaign against 40 best-practice criteria",
    "bulk-expired-domain-checker": "Check expired-domain availability and basic SEO metrics in batched queries",
    "domain-authority-checker": "Estimate domain authority from referring-domain count and quality inputs",
    "broken-link-checker": "Crawl a page and surface broken internal and outbound links with status codes",
    "bulk-url-issue-checker": "Scan many URLs at once for common issues: redirects, status, canonical, meta gaps",
    "force-google-indexing": "Step-by-step guide to nudging Google's indexer when a URL stays out of the index",
}


# ---------------------------------------------------------------------------
# Closer pools - paired with a tool/service/industry/city description.
# Each closer is a short value-prop fragment. They are slug-rotated so two
# pages of the same kind will never both pick the same closer (with high
# probability for category sizes up to ~270 items).
# IMPORTANT: closers MUST NOT contain any of the boilerplate phrases listed
# in `BANNED_PHRASES` below (those are exactly the strings that triggered
# the original user complaint). Adding a banned phrase here would defeat
# the entire fix.
# ---------------------------------------------------------------------------
TOOL_CLOSERS = [
    "Runs entirely in your browser",
    "Zero tracking, zero email gate",
    "Built for SEOs and content teams",
    "Privacy-first, instant results",
    "No upload, no API call, no signup",
    "Works on desktop and mobile",
    "Open the page, paste, get an answer",
    "Free, unlimited, and ad-light",
    "Designed for daily marketer use",
    "Sub-second results on any modern browser",
    "Use it as a sanity check before shipping",
    "Pairs with Search Console and GA4 workflows",
    "Ships JSON-LD ready output where relevant",
    "Saved bookmarks load with last input",
    "Keyboard-first, copy-paste friendly",
    "Built to match Google's documented behavior",
    "No account, no rate limit, no upsell",
    "One input, one click, one clean answer",
    "Useful for audits, briefs, and QA reviews",
    "Drop the URL or text and you are done",
]

SERVICE_CLOSERS = [
    "ROI in 90 days or we work free",
    "Senior strategists on every engagement",
    "Transparent dashboards, no black-box reporting",
    "Month-to-month with no lock-in contracts",
    "Built around your revenue goal, not vanity metrics",
    "GEO, AEO, and AIO baked into every sprint",
    "Backed by named tools and weekly delivery cadence",
    "Pricing scales with outcome, not activity",
    "Pipeline tracked back to ranked URLs",
    "Quarterly re-benchmark, no surprise upsell",
]

INDUSTRY_CLOSERS = [
    "Built for owner-operators and senior in-house leads",
    "Schema, content, and link plays tested in production",
    "Pipeline-led KPIs, not vanity ranking screenshots",
    "Local-pack, organic, and AI-citation visibility",
    "Senior practitioners, no junior account-manager hand-offs",
    "Compounding pages, not one-off campaign drops",
    "Conversion-tested copy and on-page architecture",
    "Compliance-aware copy where the vertical requires it",
    "Map pack, organic, and AI Overview coverage",
    "Audit-led roadmap with measurable 90-day milestones",
]

CITY_CLOSERS = [
    "Map pack, organic, and AI Overview coverage",
    "Local citations, schema, and landing-page mix",
    "Geo-modifier keyword coverage across districts",
    "GBP optimization and review-velocity ramps",
    "City-level competitor gap analysis included",
    "Local-pack rank tracking with weekly snapshots",
    "Tailored to the buyer mix in this metro",
    "Multilingual hreflang where the market warrants it",
    "Schema and CRO tested against local intent",
    "Pipeline tracked by neighborhood and persona",
]

COUNTRY_CLOSERS = [
    "Multi-city, multi-language coverage where it matters",
    "Region-aware schema, hreflang, and currency markup",
    "Search Console properties split per market for clean reporting",
    "Local payment, local proof, local trust signals",
    "Per-market keyword targets, not a single global list",
    "Regional review velocity and citation plays",
    "Country-level competitor benchmarks at kickoff",
]

BLOG_CLOSERS = [
    "With frameworks, examples, and templates you can apply this quarter",
    "Field-tested on live client engagements",
    "Includes the exact workflow we run inside our agency",
    "Citations, examples, and a workflow you can copy",
    "Reverse-engineered from pages that already rank and get cited",
    "A practitioner write-up, not a recycled listicle",
    "What to do this week, not theory",
]

RESOURCE_CLOSERS = [
    "Free download, no email gate",
    "Used inside live client engagements every week",
    "Plain markdown and spreadsheet, no proprietary format",
    "Update cadence: every major algorithm or AI Overview shift",
    "Pairs with the audit and brief templates linked inside",
    "Senior-built, not a recycled template marketplace upload",
]


# Boilerplate phrases that must NEVER appear in the output. These are the
# exact substrings the user flagged across pages. The audit step at the end
# of the build also greps for them and fails the build if any survive.
BANNED_PHRASES = [
    "Get a free SEO audit and grow your traffic with proven strategies",
    "Rank higher on Google and outrank competitors with proven SEO strategies",
    "Trusted by businesses worldwide for SEO, PPC, and content marketing",
    "Contact us for tailored SEO services that drive measurable growth",
    "Grow your business online with expert SEO",
    "Get a free SEO audit",
    "Win {kw} pipeline using GEO, AEO, and AIO tactics",
    "Win {NAME} pipeline using GEO, AEO, and AIO tactics",
    "run unlimited checks in your browser, no signup required",
    "Free, browser-based, unlimited",
    "Use this {NAME} to ",
    "Use this {name} to ",
    "backed by 50+ brand engagements, named tools, and pipeline-tied KPIs",
]


def _slug_to_friendly_tool_name(slug: str) -> str:
    """Convert a tool slug into a human-readable tool name when no override
    is supplied. e.g. "keyword-density-analyzer" -> "Keyword Density Analyzer"."""
    return " ".join(w.capitalize() for w in slug.split("-"))


# ---------------------------------------------------------------------------
# Industry context: per parent-category we keep 4-6 short tactic fragments
# so the composed description names something specific (not "marketing" in
# the abstract). Slug-rotated so two industries in the same parent still get
# different tactic picks.
# ---------------------------------------------------------------------------
INDUSTRY_TACTICS: dict[str, list[str]] = {
    "healthcare-medical": [
        "HIPAA-aware content and review velocity",
        "patient-acquisition funnels and condition-specific pages",
        "local-pack visibility with EEAT and trust signals",
        "schema-rich service pages tied to insurance and procedure queries",
        "compliance-vetted copy and Map Pack saturation",
    ],
    "legal-law": [
        "practice-area landing pages with bar-compliant copy",
        "legal review and citation acquisition for E-E-A-T",
        "case-type schema and intake conversion tuning",
        "local-pack visibility for attorney-near-me queries",
        "AI Overview targeting for high-intent legal questions",
    ],
    "home-services": [
        "service-area pages and Google Business Profile saturation",
        "review velocity and citation cleanup across local directories",
        "lead-form CRO and trust-signal injection",
        "seasonal demand windows with paid + organic coordination",
        "Map Pack rank tracking by ZIP and neighborhood",
    ],
    "ecommerce-retail": [
        "category and product-page templates that rank and convert",
        "structured product data with offers, ratings, and FAQ schema",
        "shopping-feed alignment with organic SEO targeting",
        "internal-link sculpting and faceted-nav indexation control",
        "AI Overview citations for product comparison queries",
    ],
    "real-estate": [
        "neighborhood landing pages and IDX-friendly internal links",
        "listing schema and review acquisition for agent EEAT",
        "buyer and seller funnel separation in content architecture",
        "Map Pack visibility for ZIP-level and city-level searches",
        "long-tail capture for niche listing modifiers",
    ],
    "saas-tech": [
        "bottom-of-funnel comparison and integration pages",
        "developer-led content for technical buyer journeys",
        "G2 / Capterra parity content with product schema",
        "AI Overview targeting for product-jobs-to-be-done queries",
        "freemium-trial conversion tracking back to organic source",
    ],
    "tech-saas": [
        "bottom-of-funnel comparison and integration pages",
        "developer-led content for technical buyer journeys",
        "AI Overview targeting for product-jobs-to-be-done queries",
        "freemium-trial conversion tracking back to organic source",
        "G2 / Capterra parity content with product schema",
    ],
    "finance": [
        "YMYL-grade EEAT signals and licensed-author bylines",
        "compliance-vetted copy on regulated products",
        "calculator and rate-table assets with structured markup",
        "AI Overview targeting on consumer-intent finance queries",
        "trust-signal saturation across NAP, citations, and reviews",
    ],
    "education": [
        "program-level landing pages with admission schema",
        "course catalog markup and faculty EEAT pages",
        "long-tail capture across degree, certificate, and bootcamp queries",
        "AI Overview targeting for student-decision questions",
        "international-student hreflang and locale routing",
    ],
    "hospitality": [
        "geo-modifier pages for amenity, district, and event queries",
        "review velocity, photo SEO, and TripAdvisor parity",
        "schema for Hotel, Restaurant, and LocalBusiness types",
        "seasonal demand windows mapped to content production",
        "AI Overview targeting for travel-decision queries",
    ],
    "hospitality-food-service": [
        "geo-modifier pages for amenity, district, and event queries",
        "review velocity and TripAdvisor parity for restaurant queries",
        "schema for Restaurant, Menu, and FoodEstablishment types",
        "seasonal demand windows mapped to content production",
        "AI Overview targeting for cuisine and dining-decision queries",
    ],
    "automotive": [
        "VIN-aware inventory pages and AutoDealer schema",
        "service-bay landing pages by location",
        "review velocity and trade-in conversion plays",
        "Map Pack visibility for make-model-near-me queries",
        "AI Overview targeting for buyer-research queries",
    ],
    "manufacturing": [
        "industry-vertical capability pages with case studies",
        "lead-form CRO for technical-buyer journeys",
        "trade-show content and PR amplification cycles",
        "structured data on capabilities, certifications, and clients",
        "AI Overview targeting for B2B specification queries",
    ],
    "professional-services": [
        "service-line landing pages mapped to revenue targets",
        "case-study libraries with measurable outcomes",
        "AI Overview targeting on buyer-research queries",
        "lead-form CRO and intake-form conversion tuning",
        "EEAT signals across author pages, reviews, and citations",
    ],
    "non-profit": [
        "donor-funnel pages and campaign landing assets",
        "schema for NonprofitOrganization with mission and beneficiary signals",
        "grant-funded content cycles tied to program outcomes",
        "Google for Nonprofits ads coordination with organic",
        "AI Overview targeting for cause-research queries",
    ],
    "nonprofit": [
        "donor-funnel pages and campaign landing assets",
        "schema for NonprofitOrganization with mission and beneficiary signals",
        "grant-funded content cycles tied to program outcomes",
        "Google for Nonprofits ads coordination with organic",
        "AI Overview targeting for cause-research queries",
    ],
    "transportation-logistics": [
        "route-pair landing pages and lane-by-lane geo modifiers",
        "schema for LogisticsService and DeliveryService types",
        "rate-table assets and quote-form CRO",
        "B2B EEAT signals on author pages and certifications",
        "AI Overview targeting for shipping-research queries",
    ],
    "retail": [
        "category and product-page templates that rank and convert",
        "store-locator pages with LocalBusiness schema",
        "review velocity and ratings parity with marketplaces",
        "shopping-feed alignment with organic SEO targeting",
        "AI Overview citations for product comparison queries",
    ],
    "ecommerce": [
        "category and product-page templates that rank and convert",
        "structured product data with offers, ratings, and FAQ schema",
        "shopping-feed alignment with organic SEO targeting",
        "internal-link sculpting and faceted-nav indexation control",
        "AI Overview citations for product comparison queries",
    ],
    "legal-services": [
        "practice-area landing pages with bar-compliant copy",
        "legal review and citation acquisition for E-E-A-T",
        "case-type schema and intake conversion tuning",
        "local-pack visibility for attorney-near-me queries",
        "AI Overview targeting for high-intent legal questions",
    ],
}

INDUSTRY_FALLBACK_TACTICS = [
    "schema-rich service pages with conversion-tested copy",
    "content velocity tied to commercial-intent keywords",
    "review and citation plays for EEAT signal saturation",
    "Map Pack and organic visibility coordination",
    "AI Overview targeting for buyer-research queries",
    "pipeline-led KPIs with weekly reporting",
]


# ---------------------------------------------------------------------------
# Public composers - one per page type. Each returns a string between
# DESC_MIN and DESC_MAX characters (best-effort; never above DESC_MAX).
# ---------------------------------------------------------------------------


def for_tool(item: dict, brand_short: str = "Shahab Abbasi") -> str:
    slug = item["slug"]
    name = item.get("name") or _slug_to_friendly_tool_name(slug)
    action = TOOL_ACTIONS.get(slug)
    closer = _pick(slug, "tcl", TOOL_CLOSERS)
    if action:
        # Lead with the action so the description names what the tool does.
        base = f"{action}"
    else:
        # Fallback for any tool not in the action map. Derive a soft action
        # from the slug suffix to avoid a "Free X" generic.
        if slug.endswith("-generator"):
            base = f"Generate {name.lower().replace(' generator','')} output from your inputs"
        elif slug.endswith(("-checker", "-tester", "-validator", "-inspector")):
            base = f"Check {name.lower().rsplit(' ', 1)[0]} against best-practice rules"
        elif slug.endswith("-calculator"):
            base = f"Calculate {name.lower().replace(' calculator','')} from your inputs"
        elif slug.endswith("-analyzer"):
            base = f"Analyze {name.lower().replace(' analyzer','')} across your inputs"
        elif slug.endswith("-optimizer"):
            base = f"Optimize {name.lower().replace(' optimizer','')} against documented best practice"
        elif slug.endswith("-tracker"):
            base = f"Track {name.lower().replace(' tracker','')} across runs and report deltas"
        elif slug.endswith("-finder"):
            base = f"Find {name.lower().replace(' finder','')} across the inputs you provide"
        elif slug.endswith("-builder"):
            base = f"Build {name.lower().replace(' builder','')} from inputs you control"
        elif slug.endswith("-counter"):
            base = f"Count {name.lower().replace(' counter','')} across any block of text"
        else:
            base = f"Free in-browser {name.lower()} for SEOs, marketers, and growth teams"
    return _compose([base, closer])


def for_service(item: dict, brand_short: str = "Shahab Abbasi") -> str:
    slug = item["slug"]
    short = (item.get("shortDescription") or "").strip()
    closer = _pick(slug, "scl", SERVICE_CLOSERS)
    # shortDescription is already unique per service.
    return _compose([short, closer])


def for_ppc(item: dict, brand_short: str = "Shahab Abbasi") -> str:
    slug = item["slug"]
    short = (item.get("shortDescription") or "").strip()
    closer = _pick(slug, "pcl", SERVICE_CLOSERS)
    return _compose([short, closer])


def for_industry(item: dict, brand_short: str = "Shahab Abbasi") -> str:
    slug = item["slug"]
    name = item.get("name") or slug.replace("-", " ").title()
    parent = item.get("parentCategory", "professional-services")
    tactics_pool = INDUSTRY_TACTICS.get(parent, INDUSTRY_FALLBACK_TACTICS)
    tactic = _pick(slug, "itc", tactics_pool)
    closer = _pick(slug, "icl", INDUSTRY_CLOSERS)
    base = f"SEO and growth marketing for {name.lower()} that runs on {tactic}"
    return _compose([base, closer])


def for_city(item: dict, country_name: Optional[str] = None, brand_short: str = "Shahab Abbasi") -> str:
    slug = item["slug"]
    name = item.get("name") or slug.replace("seo-services-", "").replace("-", " ").title()
    if country_name:
        base = f"Local SEO and paid search for {name} businesses in {country_name}"
    else:
        base = f"Local SEO and paid search for {name} businesses"
    closer = _pick(slug, "ccl", CITY_CLOSERS)
    return _compose([base, closer])


def for_country(item: dict, brand_short: str = "Shahab Abbasi") -> str:
    slug = item.get("slug") or (item.get("code") or "").lower()
    name = item.get("name") or slug.replace("-", " ").title()
    region = (item.get("region") or "").replace("-", " ")
    if region:
        base = f"SEO, paid search, and AI search visibility for businesses across {name} and the broader {region} market"
    else:
        base = f"SEO, paid search, and AI search visibility for businesses across {name}"
    closer = _pick(slug, "ncl", COUNTRY_CLOSERS)
    return _compose([base, closer])


def for_blog(item: dict, brand_short: str = "Shahab Abbasi") -> str:
    slug = item["slug"]
    title = (item.get("title") or item.get("name") or "").strip()
    kw = (item.get("primaryKeyword") or "").strip()
    closer = _pick(slug, "bcl", BLOG_CLOSERS)
    # Use the post title as the lead, varied by appended angle from primaryKeyword.
    if kw and kw.lower() not in title.lower():
        base = f"{title} - a practitioner deep dive into {kw}"
    else:
        base = f"{title} - a practitioner deep dive for senior marketers"
    return _compose([base, closer])


def for_resource(item: dict, brand_short: str = "Shahab Abbasi") -> str:
    slug = item["slug"]
    name = (item.get("name") or item.get("title") or slug.replace("-", " ").title()).strip()
    closer = _pick(slug, "rcl", RESOURCE_CLOSERS)
    base = f"{name} - the version we ship to clients, packaged for download"
    return _compose([base, closer])


def banned_phrase_in(text: str) -> Optional[str]:
    """Return the first banned phrase found in ``text`` (case-insensitive)
    or None if the description is clean."""
    t = (text or "").lower()
    for p in BANNED_PHRASES:
        if p.lower() in t:
            return p
    return None
