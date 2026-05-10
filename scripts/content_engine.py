"""Deterministic per-page content variation engine.

Given a page slug + type + entity data, produces a `unique` dict of
intro/sections/faqs/quote/metrics/keywords that's:

    1. Different on every page (sha256(slug) seeds the picks).
    2. Entity-rich (injects city/country/industry/service-specific names,
       tools, regulations, metrics, currency, neighborhoods).
    3. Expert-tone: specific numbers, named tools, year refs, decision
       trees, code snippets where appropriate.
    4. Voice-rule compliant: hyphens not em-dashes, no emojis, ROI-in-
       90-Days promise.

Templates use these via {% if unique %}...{% endif %} blocks.
"""

from __future__ import annotations

import hashlib
import random
from datetime import date, timedelta
from typing import Any


# === Seeded random helpers ===========================================
def seed_for(slug: str) -> int:
    return int(hashlib.sha256(slug.encode("utf-8")).hexdigest(), 16)


def rng_for(slug: str, salt: str = "") -> random.Random:
    return random.Random(seed_for(slug + ":" + salt))


def pick(slug: str, salt: str, options: list) -> Any:
    return rng_for(slug, salt).choice(options)


def pick_n(slug: str, salt: str, options: list, n: int) -> list:
    rng = rng_for(slug, salt)
    pool = list(options)
    rng.shuffle(pool)
    return pool[:n]


# === Entity dictionaries =============================================
COUNTRY_LANDMARKS: dict[str, list[str]] = {
    "AE": ["Burj Khalifa", "Dubai Mall", "Palm Jumeirah", "Sheikh Zayed Road", "Marina"],
    "SA": ["Kingdom Centre", "Masmak Fortress", "Al Faisaliah Tower", "Diriyah", "Riyadh Front"],
    "PK": ["Faisal Mosque", "Pakistan Monument", "Margalla Hills", "Shakarparian", "Saidpur Village"],
    "US": ["Times Square", "Golden Gate Bridge", "Lincoln Memorial", "Millennium Park", "Hollywood"],
    "GB": ["Tower of London", "Big Ben", "British Museum", "Tower Bridge", "Hyde Park"],
    "DE": ["Brandenburg Gate", "Cologne Cathedral", "Marienplatz", "Reichstag", "Englischer Garten"],
    "FR": ["Eiffel Tower", "Louvre", "Notre Dame", "Champs-Elysees", "Montmartre"],
    "ES": ["Sagrada Familia", "Park Guell", "Plaza Mayor", "Alhambra", "Las Ramblas"],
    "IT": ["Colosseum", "Duomo di Milano", "Trevi Fountain", "St Marks Basilica", "Pantheon"],
    "NL": ["Rijksmuseum", "Anne Frank House", "Vondelpark", "Erasmus Bridge", "Dam Square"],
    "PT": ["Belem Tower", "Jeronimos Monastery", "Praca do Comercio", "Sintra", "Ribeira"],
    "BR": ["Christ the Redeemer", "Sugarloaf Mountain", "Copacabana", "Avenida Paulista", "Iguazu"],
    "AR": ["Obelisco", "Casa Rosada", "Recoleta Cemetery", "Caminito", "Teatro Colon"],
    "MX": ["Zocalo", "Frida Kahlo Museum", "Chapultepec Park", "Templo Mayor", "Xochimilco"],
    "CA": ["CN Tower", "Old Quebec", "Stanley Park", "Casa Loma", "Notre-Dame Basilica"],
    "AU": ["Sydney Opera House", "Bondi Beach", "Federation Square", "Uluru", "Great Barrier Reef"],
    "JP": ["Shibuya Crossing", "Senso-ji Temple", "Tokyo Skytree", "Mt Fuji", "Fushimi Inari"],
    "KR": ["Gyeongbokgung Palace", "N Seoul Tower", "Bukchon Hanok Village", "Gangnam", "Lotte World"],
    "CN": ["Great Wall", "Forbidden City", "The Bund", "Oriental Pearl Tower", "Terracotta Army"],
    "IL": ["Western Wall", "Tel Aviv Promenade", "Old City Jerusalem", "Masada", "Bahai Gardens"],
    "EG": ["Pyramids of Giza", "Egyptian Museum", "Khan el-Khalili", "Citadel of Saladin", "Luxor Temple"],
    "TR": ["Hagia Sophia", "Blue Mosque", "Grand Bazaar", "Galata Tower", "Cappadocia"],
    "GR": ["Acropolis", "Parthenon", "Plaka", "Mykonos windmills", "Santorini"],
    "PL": ["Wawel Castle", "Old Town Square", "Lazienki Park", "Wieliczka Salt Mine", "Auschwitz Memorial"],
    "CZ": ["Charles Bridge", "Prague Castle", "Old Town Square", "Wenceslas Square", "Astronomical Clock"],
    "HU": ["Buda Castle", "Chain Bridge", "Heroes Square", "Fishermans Bastion", "Parliament"],
    "RO": ["Palace of the Parliament", "Bran Castle", "Stavropoleos Monastery", "Athenaeum", "Carpathians"],
    "DK": ["Tivoli Gardens", "Nyhavn", "Little Mermaid", "Rosenborg Castle", "Christiansborg Palace"],
    "SE": ["Gamla Stan", "Vasa Museum", "Drottningholm", "Ericsson Globe", "Skansen"],
    "NO": ["Bryggen", "Geirangerfjord", "Vigeland Park", "Holmenkollen", "Akershus Fortress"],
    "FI": ["Senate Square", "Suomenlinna", "Helsinki Cathedral", "Temppeliaukio", "Kiasma"],
    "IN": ["Taj Mahal", "India Gate", "Red Fort", "Gateway of India", "Hawa Mahal"],
    "PH": ["Intramuros", "Rizal Park", "Boracay", "Chocolate Hills", "Mayon Volcano"],
    "VN": ["Ha Long Bay", "Hoan Kiem Lake", "War Remnants Museum", "Hoi An", "Mekong Delta"],
    "TH": ["Grand Palace", "Wat Pho", "Phi Phi Islands", "Khao San Road", "Doi Suthep"],
    "MY": ["Petronas Towers", "Batu Caves", "Penang Hill", "Kek Lok Si", "Kinabalu"],
    "SG": ["Marina Bay Sands", "Gardens by the Bay", "Sentosa", "Merlion", "Orchard Road"],
    "ID": ["Borobudur", "Tanah Lot", "Mount Bromo", "Ubud", "Komodo Island"],
    "ZA": ["Table Mountain", "Robben Island", "Kruger Park", "V&A Waterfront", "Cape Point"],
    "NG": ["National Theatre", "Lekki Conservation Centre", "Eko Atlantic", "Tarkwa Bay", "Nike Art Gallery"],
    "KE": ["Maasai Mara", "Mount Kenya", "Diani Beach", "Karen Blixen Museum", "Hells Gate"],
    "NZ": ["Sky Tower", "Milford Sound", "Hobbiton", "Rotorua geysers", "Franz Josef Glacier"],
    "MA": ["Hassan II Mosque", "Jemaa el-Fnaa", "Chefchaouen", "Atlas Mountains", "Bahia Palace"],
    "QA": ["Souq Waqif", "Pearl-Qatar", "Museum of Islamic Art", "Katara", "Aspire Park"],
    "OM": ["Sultan Qaboos Mosque", "Mutrah Souq", "Al Jalali Fort", "Wadi Shab", "Nizwa Fort"],
    "BH": ["Bahrain World Trade Center", "Bahrain Fort", "Al Fateh Mosque", "Tree of Life", "Riffa Fort"],
    "KW": ["Kuwait Towers", "Grand Mosque", "Liberation Tower", "Souq Mubarakiya", "Failaka Island"],
    "JO": ["Petra", "Wadi Rum", "Dead Sea", "Jerash", "Amman Citadel"],
    "LB": ["Pigeon Rocks", "Jeita Grotto", "Baalbek", "Byblos", "Sidon Sea Castle"],
    "RU": ["Red Square", "Kremlin", "Hermitage", "Lake Baikal", "St Basils Cathedral"],
    "CO": ["Cartagena Walled City", "Monserrate", "Cocora Valley", "Plaza de Bolivar", "Tayrona"],
    "CL": ["Easter Island", "Atacama Desert", "Torres del Paine", "Valparaiso", "Plaza de Armas"],
    "PE": ["Machu Picchu", "Plaza de Armas", "Sacred Valley", "Lake Titicaca", "Nazca Lines"],
    "CH": ["Matterhorn", "Lake Geneva", "Jungfrau", "Chillon Castle", "Old Town Bern"],
    "AT": ["Schonbrunn Palace", "Stephansdom", "Hofburg", "Salzburg Old Town", "Hallstatt"],
    "BE": ["Grand Place", "Atomium", "Manneken Pis", "Bruges canals", "Mini-Europe"],
}


COUNTRY_NEIGHBORHOODS: dict[str, list[str]] = {
    "default": ["central business district", "waterfront", "old town", "innovation quarter", "creative district", "financial district", "luxury retail strip", "tech hub", "university quarter", "harbor side", "high street", "design district"],
}


REGULATIONS: dict[str, list[str]] = {
    "healthcare-medical": ["HIPAA compliance", "GDPR for patient data", "FTC truthfulness rules", "HHS OCR safe harbor", "FDA marketing guidance"],
    "legal-services": ["bar association advertising rules", "ABA Model Rule 7.1-7.5", "ALI compliance", "state-specific solicitation rules", "legal disclaimer requirements"],
    "finance": ["FINRA Rule 2210", "SEC marketing rule (206(4)-1)", "AML/KYC", "PCI-DSS for payment data", "GDPR/CCPA"],
    "real-estate": ["NAR Code of Ethics", "Fair Housing Act", "RESPA", "MLS rules", "state license advertising rules"],
    "ecommerce": ["FTC truth-in-advertising", "GDPR consent banners", "PCI-DSS", "consumer rights directives", "CAN-SPAM"],
    "tech-saas": ["SOC2", "ISO 27001", "GDPR DPA", "data residency", "EU AI Act"],
    "education": ["FERPA", "COPPA", "Title IX", "accreditor disclosure", "state authorization for distance learning"],
    "hospitality-food-service": ["health-department permits", "ADA compliance", "alcohol licensing", "menu nutrition disclosure", "OSHA"],
    "home-services": ["state contractor licensing", "lead-paint RRP rule", "OSHA safety", "EPA refrigerant rules", "consumer protection"],
    "transportation-logistics": ["DOT/FMCSA", "IATA cargo rules", "customs broker license", "ELD mandate", "ISO 9001"],
    "professional-services": ["industry-body code of conduct", "state license advertising rules", "client-confidentiality covenants", "GDPR/CCPA", "FTC endorsement guides"],
    "retail": ["FTC labeling rules", "PCI-DSS", "GDPR/CCPA", "state weight-and-measure rules", "ADA web accessibility"],
    "nonprofit": ["IRS 501(c)(3) advertising", "state registration", "donor-data privacy", "GDPR for cross-border donations", "FCC/CRTC for fundraising calls"],
}


PERSONAS: dict[str, list[str]] = {
    "healthcare-medical": ["practice owner", "operations director", "patient acquisition lead"],
    "legal-services": ["managing partner", "marketing partner", "intake director"],
    "finance": ["CMO", "head of growth", "compliance lead"],
    "real-estate": ["broker-owner", "team lead", "transaction coordinator"],
    "ecommerce": ["DTC founder", "head of acquisition", "performance-marketing lead"],
    "tech-saas": ["VP marketing", "demand-gen lead", "product marketing manager"],
    "education": ["enrollment director", "marketing dean", "admissions head"],
    "hospitality-food-service": ["GM", "owner-operator", "marketing director"],
    "home-services": ["owner-operator", "GM", "fleet dispatcher"],
    "professional-services": ["managing director", "rainmaker partner", "marketing principal"],
    "retail": ["store-group owner", "ecomm head", "merchandising lead"],
    "transportation-logistics": ["fleet operations director", "head of growth", "regional GM"],
    "nonprofit": ["executive director", "development director", "comms lead"],
    "default": ["owner", "head of marketing", "growth lead"],
}


SERVICE_TOOLS: dict[str, list[str]] = {
    "technical-seo": ["Screaming Frog", "Sitebulb", "Lighthouse", "PageSpeed Insights", "Google Search Console", "Ahrefs Site Audit", "Botify", "DeepCrawl"],
    "content-strategy": ["Surfer SEO", "Frase", "MarketMuse", "Clearscope", "Ahrefs Keyword Explorer", "AnswerThePublic"],
    "seo-content-strategy": ["Surfer SEO", "Frase", "MarketMuse", "Clearscope", "Ahrefs Keyword Explorer", "AnswerThePublic"],
    "link-building": ["Ahrefs", "Pitchbox", "BuzzStream", "Hunter.io", "Respona", "Postaga"],
    "local-seo": ["Local Falcon", "BrightLocal", "GBP Insights", "Whitespark", "Yext", "Moz Local"],
    "international-seo": ["Hreflang Tags Tester", "Distill.io", "DeepL", "Yandex Webmaster", "Naver Webmaster", "Baidu Webmaster"],
    "ecommerce-seo": ["Shopify Search Insights", "Klaviyo", "Triple Whale", "Northbeam", "Ahrefs", "Lighthouse"],
    "saas-seo": ["Ahrefs", "Clearscope", "ChartMogul", "Mixpanel", "PostHog", "Search Console"],
    "ppc-management": ["Google Ads Editor", "Microsoft Ads", "Optmyzr", "Adalysis", "Google Tag Manager", "Looker Studio"],
    "geo-aeo": ["Perplexity Pro", "ChatGPT Search", "Profound", "Otterly.ai", "ZipTie", "Athena"],
    "default": ["Ahrefs", "Screaming Frog", "Google Search Console", "GA4", "Looker Studio", "Surfer SEO"],
}


METRIC_TARGETS: dict[str, str] = {
    "lcp": "Largest Contentful Paint under 2.5 seconds (75th percentile mobile)",
    "inp": "Interaction to Next Paint under 200 milliseconds",
    "cls": "Cumulative Layout Shift under 0.1",
    "ttfb": "Time to First Byte under 600 milliseconds",
    "fcp": "First Contentful Paint under 1.8 seconds",
    "crawl_budget": "indexable URLs / total URLs above 0.85",
    "internal_links": "minimum 3 internal links per money page within 1-click of the homepage",
    "ai_citations": "branded mentions across at least 4 of: ChatGPT Search, Perplexity, Claude, Gemini, Bing Copilot",
}


# === Page-type-specific copy generators ==============================
SERVICE_INTRO_TEMPLATES = [
    "If you treat {NAME} as a checklist, you will lose. Real growth comes from compounding decisions: which queries get a page, which pages get internal links, which links earn citations from large language models, and which citations end up in front of buyers searching from {SAMPLE_CITY}, {SAMPLE_CITY_2}, or any of the {COUNTRY_COUNT}+ markets we operate in. Our {NAME} engagement is the engine for that compounding.",
    "{NAME} in 2026 is no longer about ranking page one for a single keyword. It is about being the cited answer when a buyer asks ChatGPT, Perplexity, or Google AI Overviews a question that overlaps your offer. To get there, you need a clean technical foundation, a content graph that mirrors how AI models reason about your niche, and a link profile that signals authority to both Google and to LLM training crawlers. That is what we deliver.",
    "Most {NAME} programs stall because the agency optimizes for activity, not for compounding revenue. We build the program backwards: start from the revenue target, work back to the keyword cluster that produces that revenue, then engineer the on-site, off-site, and AI-visibility work to capture it. Every quarter we re-benchmark to make sure the program is still on track.",
    "Buyers no longer scroll a list of ten blue links. They ask a question, get an answer with a few cited sources, and click through if they want detail. Our {NAME} discipline is built for that reality: structured content with extractable answers, schema that machines can read, internal linking that signals topical authority, and trust signals that survive the LLM crawl.",
    "There are dozens of {NAME} agencies in {COUNTRY_NAME} alone. The reason brands pick {BRAND} is not the deck or the dashboard - it is that we put a 90-day ROI guarantee in writing. If we miss the milestone, we work free until we hit it. Few firms will sign that clause. We do, because the system we run hits its targets.",
    "{NAME} is the most measurable channel in marketing. Every dollar in produces a traceable lift in indexed pages, ranked queries, organic sessions, branded searches, and pipeline. We stitch all five of those layers into one revenue dashboard so executives stop arguing about whether {NAME} works and start arguing about how fast to scale it.",
    "Across {COUNTRY_COUNT}+ markets and {INDUSTRY_COUNT}+ verticals, the lever that consistently moves revenue is {NAME} done with operator discipline rather than agency cliches. Our team treats {NAME} as a system: an audit produces a backlog, the backlog produces a sprint plan, the sprint plan produces shippable artifacts, and the artifacts produce ranked URLs that earn pipeline.",
    "Founders we work with often ask why they should pay for {NAME} in 2026 when AI has supposedly killed search. The answer is that the AI engines themselves are search engines, and they reward the same fundamentals: structured content, entity disambiguation, internal linking, and authoritative citations. Our {NAME} program ships all four against your top 200 commercial queries.",
    "We benchmark every {NAME} engagement against three numbers: time to first ranking lift (target: under 60 days), time to revenue inflection (target: under 120 days), and 12-month return on retainer spend (target: 4x or better). All three are tracked publicly inside our client dashboards.",
    "{NAME} works because of compounding. Year one sets the foundation, year two flexes the curve, year three is when most clients realize they have moved from chasing demand to harvesting it. We design every engagement so the steepest part of the curve is in front of you, not behind you.",
    "The {NAME} discipline most agencies sell in 2026 is the same one they sold in 2018, with a few buzzwords swapped. Ours is rebuilt from first principles every quarter as the ranking algorithms, AI engines, and buyer behaviors evolve. We update the playbook in public so you can see what changed and why.",
    "There is an honesty problem in {NAME}. Most agencies promise rankings they cannot deliver, hide behind vanity metrics, and bill on activity rather than outcome. We bill on outcome, share the dashboards in real time, and put a 90-day ROI guarantee in writing. The clients who care about that math are the ones we serve well.",
    "Buyers in your category do not buy SEO. They buy revenue. {NAME} is the channel that produces it. Our job is to compress the time between effort and outcome by sequencing the work in the order that earns ranked URLs fastest. Specifics: technical fixes in week 1, content roadmap in week 2, first 6 articles live by week 4, internal-link graph complete by week 8.",
    "Every {NAME} engagement we sign starts with a forensic audit of the past 24 months of organic data. Most sites have leaks the previous owner did not see: cannibalization between pages, wrong canonicals, missing FAQ schema, broken internal links, orphan content. The first 30 days fixes those. The next 11 months compounds.",
    "{NAME} in your category does not have to mean copying the playbook of the market leader. It often means finding the specific keyword cluster the market leader has not yet defended and dominating that cluster before they notice. Our {NAME} strategists are unusually good at finding that cluster.",
]

SERVICE_INTRO_TEMPLATES_2 = [
    "Below, we outline how the {NAME} program runs week by week, what the deliverables look like, and how we measure ROI without resorting to vanity metrics.",
    "The remainder of this page covers the {NAME} delivery stack we use, the metrics we benchmark every engagement against, and the pricing tiers that fit different stages of growth.",
    "If you are evaluating {NAME} agencies, the rest of this page is built to give you the operator-level details that proposals usually leave out: tooling, weekly cadence, reporting structure, and renewal terms.",
    "The sections below walk through what {NAME} actually looks like in practice for a brand in your stage: the first 30 days, the 90-day inflection, the 12-month curve, and what we do when the program plateaus.",
    "Read on for the {NAME} delivery framework: discovery, audit, strategy, execution, measurement. Each phase has a deliverable, a target, and a measurable outcome we benchmark publicly.",
    "Keep scrolling for the unfiltered version of how we run {NAME}: the tools, the metrics, the weekly cadence, and the line items that show up in your monthly invoice.",
    "{TOOLS_PRIMARY} feature heavily in our stack. So do {TOOLS_SECONDARY}. Below we explain why each one earns its place and how the pieces fit together into a measurable system.",
    "On the next few sections, we cover the discrete decisions a {NAME} buyer should make in 2026: in-house vs agency vs hybrid, which retainer tier to start at, and what success looks like at week 1, week 12, and week 52.",
]

INDUSTRY_INTRO_TEMPLATES = [
    "Generic SEO frameworks do not transfer to {NAME}. The buying journey is different, the trust signals are different, the compliance constraints are different, and the keyword shape is different. Our {NAME} program is built around the specific way {PERSONA} actually search, evaluate, and decide.",
    "{NAME} marketing has two failure modes: copy that gets the brand sued for compliance, and copy that gets ignored by buyers who can spot generic content from a paragraph away. Our {NAME} content team has shipped material reviewed by {REGULATION} attorneys, with the conversion data to prove it still pulls.",
    "If you run a {NAME} business, your competition is not just other {NAME} firms - it is aggregators, marketplaces, and editorial publishers who outspend you on content. The way to win is not to outspend them but to out-position them: own the long-tail queries they ignore and own the entity graph that AI engines use to recommend providers.",
    "We map every {NAME} engagement to a {PERSONA} buying journey: awareness, consideration, evaluation, decision, retention. Each stage gets a content set, a schema layer, and a measurement plan. By month three, you can see exactly which stage your pipeline gets stuck on and we redirect resources to fix it.",
    "{NAME} is regulated. {REGULATION} matters. Our process bakes compliance review into every brief so legal does not become the bottleneck that kills launch velocity. The result: 4 to 6 weeks from kickoff to first piece live, instead of the 12 to 16 weeks most firms accept as normal.",
    "The trust threshold for {NAME} buyers is unusually high. Reviews matter more than they do in other categories. Branded search volume matters more. Local presence matters more. Our {NAME} program optimizes all three explicitly with measured outcomes inside 90 days.",
    "Most agencies pitch {NAME} marketing as a tactical question (channels, budgets, ad copy). It is actually a positioning question. Until your offer is differentiated against the {PERSONA_2} top alternatives, no amount of {NAME} content fixes the conversion problem. Our intake process forces that work first.",
    "We turn down about 60 percent of {NAME} prospects because their unit economics will not support an SEO retainer. The 40 percent we accept consistently hit the 90-day ROI milestone. The criteria we use for that filter are explicit, public, and on the engagement page.",
    "{NAME} buyers are unusually skeptical of generic agency pitches because their category is targeted by lookalike spammers (we have seen the same 'we will rank you #1' deck circulating across {NAME} firms for three years). Our pitch starts with the data, not the deck.",
    "Across the {NAME} engagements we have run since 2020, the same three patterns repeat: thin service-area pages, missing schema, undercooked review system. Closing those three gaps is worth 30 to 60 percent ranking lift on its own, before any net-new content ships.",
    "The fastest way for a {NAME} brand to lose money in 2026 is to ship generic AI-written content. The fastest way to compound revenue is to ship operator-written, compliance-reviewed, schema-rich content that earns citations from both Google and the AI answer engines. Our team produces the second kind.",
]
INDUSTRY_INTRO_TEMPLATES_2 = [
    "The sections that follow walk through the {NAME} buyer journey, the schema layer we install, and the compliance workflow we use so legal review becomes a 24-hour cycle instead of a 4-week one.",
    "Below, we cover the {NAME}-specific KPIs we track, the typical content investment per quarter, and the pricing tiers that fit a {NAME} brand at different stages of growth.",
    "Read on for the {NAME} growth playbook: the audit checklist we run on day one, the schema markup we install on day three, the first 6 article briefs we ship by week 4, and the measurement framework we lock in by week 8.",
    "The rest of this page is built for {PERSONA_1} who are evaluating whether to bring {NAME} marketing in-house, hire an agency, or run hybrid. We cover the tradeoffs, the typical costs, and where each model breaks down.",
    "Keep scrolling for the unfiltered version of how we run {NAME} marketing in 2026: the regulations, the personas, the schema, the metrics, and the cadence.",
    "If you are evaluating agencies for {NAME}, the rest of this page gives you the operator-level details proposals usually leave out: the writers' qualifications, the editor review pass, the compliance review cycle, and the renewal terms.",
]

CITY_INTRO_TEMPLATES = [
    "Doing SEO in {NAME} without an on-the-ground partner is like hunting in the dark. The Map Pack is not the same as it is in {COUNTRY_NAME}'s capital, the citation directories that actually move the needle are not the same as in the rest of the country, and the LSI keywords that buyers in {NAME} use have local idioms that generic agencies miss. We have run campaigns across {NAME} since 2020 and our playbook is calibrated to {NAME} buyer behavior.",
    "{NAME} is one of the most competitive local search markets in {COUNTRY_NAME}. Hundreds of businesses in your category are chasing the same Map Pack slots, and the bar for content quality keeps rising. To break through, you need three things working together: a Google Business Profile optimized for {NAME} ZIP codes, citations on directories that actually rank, and a review velocity that beats your top three competitors. We ship all three.",
    "Buyers in {NAME} no longer search the same way they did even two years ago. AI answer engines now intercept commercial-intent queries before the user reaches the SERP, which means your business has to be cited in the answer or it does not get the click. Our {NAME} program treats AI visibility as equal in priority to Google rankings.",
    "If your business serves {NAME} customers, you have a measurable home advantage you can compound: proximity, language, payment-method preferences, regulatory familiarity, and local trust signals. Our local SEO program for {NAME} converts that advantage into Map Pack placement, organic ranking, and AI citations.",
    "We have audited more than 100 {NAME}-area sites in the past two years. The patterns are clear: most local businesses leave 40 to 60 percent of their organic potential on the table because of preventable technical issues, missing schema, and stale Google Business Profiles. Our {NAME} engagement closes those gaps within the first 30 days and then scales from there.",
    "Local SEO in {NAME} comes down to four assets: a Google Business Profile that wins the proximity battle around {LANDMARK_1}, a service-area page set tuned to neighborhoods like {NEIGHBORHOOD_1}, a citation footprint that aligns NAP across the directories that matter in {COUNTRY_NAME}, and a review velocity that beats the top three competitors in your category. We ship all four inside 60 days.",
    "{NAME} buyers behave differently from buyers in other {COUNTRY_NAME} cities. Their search queries blend {LOCAL_LANGUAGE} idioms with English brand names, they rely heavily on {DOMINANT_REVIEW_SITE} for trust signals, and they convert at higher rates from mobile than desktop. Our {NAME} program is calibrated to all three patterns.",
    "If your competition in {NAME} is national chains and franchises, the path is different from competing against local independents. National chains usually have stronger backlink profiles and weaker local relevance signals - which means an aggressive Map Pack play wins the local pie back. We have run that exact play in {NAME} for clients in {INDUSTRY_HINT}.",
    "{NAME} is the kind of market where 'almost good enough' SEO loses to 'fully sharpened' SEO every time. The top three Map Pack slots in {NAME} are won by businesses with 4.7+ star averages, 200+ recent reviews, weekly Google Posts, and exhaustive service-area pages. If you are missing any one of those, you are leaving Map Pack revenue on the table.",
    "Brands operating in {NAME} need an SEO program that respects local context: the timezone is {TIMEZONE}, the currency is {CURRENCY}, transactions clear in {LOCAL_PAYMENT_METHODS}, and trust signals lean heavily on locally recognized publications and review platforms. We do not run an offshore content shop. Our {NAME} content is briefed by operators who actually know your market.",
]
CITY_INTRO_TEMPLATES_2 = [
    "Below we walk through the {NAME}-specific playbook: the GBP optimization checklist, the citation directories that move the needle in {COUNTRY_NAME}, the review velocity targets, and the service-area page architecture.",
    "The remainder of this page covers what we do for {NAME} businesses week by week, the metrics we benchmark publicly, and the pricing tiers that fit local independents through to multi-location operators.",
    "Read on for the unfiltered version of how we approach {NAME} local SEO: the audit, the schema, the GBP, the reviews, the citations, the content, and the measurement.",
    "Keep scrolling for {NAME}-specific deliverables, KPIs, and pricing. If you serve customers across multiple {COUNTRY_NAME} cities, the multi-location section near the bottom is the one to read first.",
    "Below, we cover the four-week onboarding for {NAME} clients: discovery (week 1), audit and benchmark (week 2), GBP and schema deployment (week 3), and first content sprints (week 4).",
]

COUNTRY_INTRO_TEMPLATES = [
    "Running an SEO program across {NAME} requires more than translation. You need to understand the local link directories, the dominant payment methods, the trust badges buyers expect, the regulatory framework around marketing claims, and the seasonal demand patterns that move 30 to 50 percent of the annual revenue. Our {NAME} country program covers all of it.",
    "{NAME} is not a single market - it is a federation of regional buyer behaviors. The Map Pack in the capital is not the same as in the secondary cities, the YouTube and TikTok dynamics differ by region, and the language variant on the page can change conversion by 20 percent. Our country playbook ships all of these dimensions.",
    "We have engineered SEO programs for brands operating across {NAME} since 2020. The fastest path to compounding growth is to dominate one regional cluster (typically the capital plus 2 to 3 satellite cities) and then expand outward. Our 90-day onboarding includes a regional priority map so you spend dollars where they pay back fastest.",
    "Most agencies treat {NAME} as a single SEO market. They miss the regional variance and ship a flat keyword set. We map your offer to {NAME} regional buyer journeys, then build city-level landing pages that capture both organic search and Google Maps demand within each region.",
    "If your brand operates across {NAME}, the SEO question is rarely 'what keyword' and almost always 'what city to defend first'. Our country onboarding produces an explicit city priority queue so retainer dollars compound in the markets that pay back fastest.",
    "{NAME} has its own dominant review platforms, citation directories, and trust signals. Generic agencies treat the country like a smaller US: same Yelp, same BBB, same workflows. That misses 40 to 60 percent of the local trust graph that actually moves rankings here.",
]
COUNTRY_INTRO_TEMPLATES_2 = [
    "The sections below break down the {NAME} country playbook: regional priority queue, city-level landing page templates, citation directory list, schema markup specific to local commerce, and reporting cadence.",
    "Read on for the {NAME} country plan: regional research, capital-first sequencing, citation strategy, content calendar by region, and measurement framework.",
    "Below we cover what {NAME} brands typically miss when they hire an offshore agency: the local citation directories, the regional review platforms, the language variant on landing pages, and the regulatory framing of marketing claims.",
    "Keep scrolling for the {NAME} regional roadmap: which cities to defend first, which to enter second, and which to deprioritize until the program produces compounding revenue.",
]

BLOG_INTRO_TEMPLATES = [
    "We wrote this guide for the {AUDIENCE} who are tired of hand-wavy {TOPIC} content. Every recommendation below has been pressure-tested on real client engagements with measurable revenue outcomes. Where we cite a number, the source is in the footnote. Where a tactic stopped working in 2025, we say so.",
    "{TOPIC} changed in 2026. The frameworks that worked before AI Overviews are not the frameworks that work now. This piece walks through the 2026-current version of the playbook, with the specific schemas, internal-link patterns, and AI-visibility tactics that we are using on live client work this quarter.",
    "Most {TOPIC} guides on Google are reverse-engineered from the same five blog posts that ranked in 2022. We refused to do that. This is a synthesis of 2025 and 2026 first-party data from our client engagements: which interventions moved the needle, which did not, and which ones produced unexpected second-order effects.",
    "If you have already read three articles on {TOPIC}, you do not need another high-level overview. You need the operator-level details: the SQL queries, the GSC filters, the schema markup, the internal-link distance budget. We put all of that here.",
    "There is a generation of {TOPIC} content on the open web that was good in 2022 and is now actively misleading. We wrote this guide to replace it with the 2026 operator's view. If you find anything below that contradicts your current playbook, we welcome the email - we link the original source on every claim.",
    "We publish on {TOPIC} only when our team has shipped real client work that contradicts the public consensus and we have measured outcomes for it. This piece is one of those. Read it as a critique of common practice, not a confirmation of it.",
    "Search visibility in 2026 is determined by three layers stacking: the technical layer, the entity layer, and the AI-citation layer. {TOPIC} is one of the disciplines where all three layers intersect. We walk through each one with examples from live engagements.",
]
BLOG_INTRO_TEMPLATES_2 = [
    "By the end of this article, you will know exactly which {TOPIC} interventions to prioritize this quarter, which to defer, and which to drop. We provide a one-page action list at the end.",
    "Below, you will find the framework, the templates, the gotchas, and the exact decisions we walked through with our most recent client engagements. Bring this guide to your next planning meeting.",
    "If you would rather watch us run through this {TOPIC} playbook with you on a 20-minute call, the booking link is at the bottom. The article works as a self-serve substitute too.",
    "We refresh this guide quarterly. The version you are reading was last updated to reflect 2026 algorithm and AI-engine behaviors. Older versions are archived under the same URL.",
    "Read straight through, or jump to the section relevant to your stage: foundations, intermediate, or advanced.",
]

RESOURCE_INTRO_TEMPLATES = [
    "We built {NAME} for our own client work, then realized other operators would benefit from the same artifact. So we cleaned it up, removed the client-specific bits, and made it free. No email gate. No upsell.",
    "Most templates you find online for {TOPIC} are written by people who have never run a real engagement. {NAME} comes from running 100+ live client programs across 22 languages and 78 countries. Every section earned its place because it solved a real problem on a real engagement.",
    "{NAME} compresses a 90-day learning curve into a single PDF. By the time you finish working through it, you will have produced the same artifact a senior consultant would charge $3,000 to produce.",
    "There are dozens of free templates and checklists for {TOPIC} on the open web. Most are 2019-vintage thinking with a fresh coat of paint. {NAME} is the 2026 operator's version, written by a team that ships this work for paying clients every week.",
    "{NAME} is the artifact we wished existed when we started running {TOPIC} engagements ourselves. So we built it, used it on 50+ client projects, refined it through real outcomes, and then released it under a permissive license.",
    "If you are running {TOPIC} solo or with a small team, {NAME} eliminates the part of the work that is rote and frees you to focus on the part that is judgment-heavy. It does not replace strategy. It replaces the manual labor around strategy.",
]
RESOURCE_INTRO_TEMPLATES_2 = [
    "Below we cover what is inside {NAME}, who it is for, the time-to-implement, and the typical outcomes operators see in the first 30 days of using it.",
    "Read on for the full table of contents of {NAME}, the prerequisites we recommend, and links to the related artifacts in our resource library.",
    "Keep scrolling for download instructions, the changelog (we update this resource quarterly), and the case studies of operators who have used it on live engagements.",
    "The sections below describe how to use {NAME} in your environment, how to extend it for a multi-team workflow, and how to plug its outputs into your reporting stack.",
]

TOOL_INTRO_TEMPLATES = [
    "{NAME} is built for one job: give you a fast, accurate answer without making you sign up for anything or watch ads. Everything runs in your browser. Nothing gets sent to a server.",
    "We built {NAME} because the existing online tools for this job either gate the result behind an email signup, log every input you submit, or are inaccurate. None of those are acceptable. So we built our own and made it free.",
    "If you use {NAME} every week, consider it free forever. We do not run ads on this page, do not sell your data, and do not monetize the tool. It exists so that {AUDIENCE} have a faster way to do their job.",
    "{NAME} is engineered for the specific workflow {AUDIENCE} run dozens of times a week. The interface is built to give a correct answer in three clicks or less. We removed every step that was not strictly necessary.",
    "Most online tools for this task are slow, ad-cluttered, or wrong on edge cases. {NAME} is fast, has zero ads, and handles edge cases that we explicitly tested against the W3C and Google reference implementations.",
    "{NAME} replaces the spreadsheet you would otherwise have to build to do this calculation. It is faster, more correct on edge cases, and produces output you can paste directly into your CMS.",
]
TOOL_INTRO_TEMPLATES_2 = [
    "Below we cover the inputs the tool accepts, the outputs it produces, the edge cases we have explicitly tested, and the common use cases {AUDIENCE} report.",
    "Read on for the methodology, the assumptions baked into the calculation, and the places where the tool will not give you a correct answer (so you can use a more specialized tool when needed).",
    "Keep scrolling for use cases, the underlying formulas, integration tips, and a link to our open-source repository where the tool source lives.",
    "The sections below explain how {NAME} fits into a broader {AUDIENCE} workflow, what tools to combine it with, and how to interpret the outputs in different contexts.",
]


SERVICE_SECTION_VARIANTS: list[dict] = [
    {
        "h2": "How {NAME} compounds revenue (the math)",
        "body": (
            "Most agencies sell {NAME} as a project. We sell it as a compounding asset. Year one, the program produces about "
            "{Y1_TRAFFIC} new monthly organic sessions. Year two, those pages mature and the same content set produces "
            "{Y2_TRAFFIC} sessions. Year three, the most authoritative pages have aged into top-of-funnel default destinations "
            "for buyer queries and the program produces {Y3_TRAFFIC} sessions on the same content investment. The "
            "discount-to-revenue conversion is the multiplier you optimize for. We model it for your category before "
            "we send a proposal."
        ),
    },
    {
        "h2": "The {NAME} delivery stack we run on every engagement",
        "body": (
            "We are tool-agnostic by stage but opinionated by tool: {TOOLS}. Each one earns its place because it surfaces "
            "data the others miss. We use {TOOLS_PRIMARY} for the audit phase, {TOOLS_SECONDARY} for the execution phase, "
            "and a custom Looker Studio + GA4 pipeline for the reporting layer. You see the same dashboards we do. There "
            "is no black-box agency report."
        ),
    },
    {
        "h2": "What {NAME} looks like at week 1, week 4, week 12, week 24",
        "body": (
            "Week 1: kickoff + audit + access setup. Week 4: top-priority technical fixes shipped, content roadmap signed off, "
            "first 4 to 6 articles in flight. Week 12: 18 to 24 articles live, internal-link graph complete, schema implemented, "
            "first ranking lift visible. Week 24: pipeline attribution dialed in, AI-citations graph plotted, second 24-article "
            "batch in flight. Most clients see compounding lift starting month 4."
        ),
    },
    {
        "h2": "Why {NAME} is different from generic SEO in 2026",
        "body": (
            "Generic SEO is built around the assumption that buyers see a SERP and click a result. That assumption is "
            "now wrong on more than half of commercial queries. AI Overviews, ChatGPT Search, Perplexity, and Bing Copilot "
            "now intercept the query and serve the answer. Our {NAME} program optimizes for being cited in that answer, "
            "not just ranked beneath it. The difference is structured content, extractable answers, and schema that "
            "machines can reason about."
        ),
    },
    {
        "h2": "Performance benchmarks we hit on every {NAME} engagement",
        "body": (
            "Core Web Vitals: {CWV_LCP}, {CWV_INP}, {CWV_CLS}. Crawl budget: {CRAWL_BUDGET}. Internal linking: {INTERNAL_LINKS}. "
            "AI visibility: {AI_CITATIONS}. We treat these as non-negotiables. If a deliverable does not meet the threshold, "
            "we redo it. No surcharge. The whole point of paying for {NAME} is that the foundation is right."
        ),
    },
    {
        "h2": "Common {NAME} mistakes we fix in week one",
        "body": (
            "We have audited more than 200 mid-market sites in the past 18 months. The same mistakes show up over and over: "
            "thin product pages with no FAQ schema; orphaned cluster content (no internal links pointing in); duplicate-page "
            "issues from faceted navigation; missing or wrong hreflang on multi-language sites; and broken canonicals on "
            "pagination. We ship a fix patch in the first 7 to 10 days that closes 60 to 80 percent of these on most sites."
        ),
    },
    {
        "h2": "How we measure {NAME} ROI (and why it survives a CFO review)",
        "body": (
            "We attribute revenue at the page level. Each landing page is mapped to a UTM-tagged conversion path, every "
            "form fill or call gets stamped with the entry page, and our pipeline dashboard surfaces revenue closed by "
            "page. By month three, your CFO can ask 'what is the dollar return on this content?' and you have the answer "
            "in seconds. It is the same query model we run for our own retainer book."
        ),
    },
    {
        "h2": "How {NAME} interacts with paid media and email",
        "body": (
            "Most teams run SEO, paid, and lifecycle as silos. We do not. The keyword data from {NAME} feeds the paid-search "
            "negative-keyword list, the content topics fuel the email-nurture sequences, and the landing-page wins from "
            "paid get folded back into the SEO content calendar. The cross-channel lift is usually 1.4 to 1.8x the lift "
            "of any single channel run alone."
        ),
    },
    {
        "h2": "Choosing the right {NAME} retainer tier",
        "body": (
            "If you have 0 to 10 employees and target a single regional market, the Foundation tier ($1,750/mo) gets you "
            "to first page on long-tail queries within 90 days. If you operate across 2 to 5 markets and have a competing "
            "brand outranking you, Growth ($4,500/mo) is the right tier. If you are a national or multinational brand "
            "with a competitive enterprise category, Authority ($12,500+/mo) is what hits the timeline. We will tell you "
            "which tier fits before you sign anything."
        ),
    },
    {
        "h2": "What changes if you have already run {NAME} before",
        "body": (
            "If you have a previous agency relationship that did not deliver, the first thing we do is a forensic audit of "
            "what shipped. Most prior work has 30 to 50 percent salvageable assets that just need re-purposing. We do not "
            "throw it away to inflate scope. The leverage is in fixing the gaps, not rebuilding from zero."
        ),
    },
    {
        "h2": "{NAME} for AI search engines (the GEO and AEO layer)",
        "body": (
            "Generative Engine Optimization (GEO) and Answer Engine Optimization (AEO) are the two new disciplines that "
            "ride on top of classical SEO. GEO targets ChatGPT, Perplexity, Gemini, and Claude. AEO targets voice answers "
            "and featured snippets. Our {NAME} program ships both: structured FAQ schema, Speakable schema, "
            "clear-question-clear-answer paragraph patterns, and the entity graph that LLM training pipelines actually "
            "reward."
        ),
    },
]

CITY_SECTION_VARIANTS: list[dict] = [
    {
        "h2": "How buyers in {NAME} actually search in 2026",
        "body": (
            "Buyers in {NAME} blend three discovery surfaces: Google Maps, classical Google search, and AI answer engines. "
            "Map Pack queries dominate same-day intent (`{NAME_LOWER} near me`, `best {INDUSTRY_KW} in {NAME}`). Classical "
            "search dominates research-stage intent (`{INDUSTRY_KW} {NAME} reviews`). AI answer engines now intercept "
            "the comparison-stage queries (`how do I choose a {INDUSTRY_KW} in {NAME}`). Our local program ships a content "
            "and schema layer for each of these surfaces."
        ),
    },
    {
        "h2": "The {NAME} Map Pack: what actually moves the needle",
        "body": (
            "We have audited the {NAME} Map Pack across 12+ verticals. The pattern is consistent: top three placements "
            "share three things. First, a Google Business Profile with the primary category nailed and 4+ secondary "
            "categories filled. Second, citations across {COUNTRY_NAME}-specific directories (not just Yelp). Third, a "
            "review velocity above 8 reviews per month with at least 30 percent of reviews containing the primary "
            "service keyword in the body. We ship all three."
        ),
    },
    {
        "h2": "Neighborhoods and landmarks in {NAME} we target with content",
        "body": (
            "Within {NAME}, we tier neighborhoods by commercial density and competition. The first wave usually includes the "
            "{LANDMARK_1}, {LANDMARK_2}, and {LANDMARK_3} catchment areas. From there we expand to lower-competition "
            "neighborhoods where conversion rates are often 30 to 60 percent higher because fewer competitors target "
            "those queries. Our service-area pages cover both."
        ),
    },
    {
        "h2": "Citations and directories that matter in {NAME}",
        "body": (
            "Generic citation lists do not work in {NAME}. The directories that actually pass authority and drive traffic "
            "are local-language ones (in {COUNTRY_NAME}), industry-specific ones, and paid local sponsorships of community "
            "organizations. Our citation build for {NAME} ships 40 to 80 high-quality entries in the first 60 days, all of "
            "which we monitor monthly for NAP consistency drift."
        ),
    },
    {
        "h2": "Currency, payment, and trust signals for {NAME} buyers",
        "body": (
            "Buyers in {NAME} expect to see {COUNTRY_CURRENCY} pricing on the page (not USD-converted at the time of view), "
            "to see payment methods popular in the region, and to see trust badges that the local market recognizes. "
            "Localizing these three signals usually lifts conversion 12 to 25 percent on otherwise identical pages."
        ),
    },
    {
        "h2": "Reviews, reputation, and review velocity for {NAME}",
        "body": (
            "We treat reviews as a marketing channel, not a hygiene checkbox. Our system asks every closed deal for a review "
            "via SMS within 24 hours of a positive milestone, routes responses through a sentiment classifier, and surfaces "
            "the highest-leverage reviews to the response queue. Result: review velocity that beats your top {NAME} "
            "competitor in 90 days."
        ),
    },
    {
        "h2": "Common technical issues we find on {NAME} sites",
        "body": (
            "On the {NAME} sites we audit, the recurring issues are: missing or wrong LocalBusiness schema, missing FAQ "
            "schema, slow LCP from unoptimized hero images, duplicate URLs from session parameters, and missing hreflang "
            "tags on multi-language locations. The fix patch usually takes 7 to 10 engineering days and closes 60 to 80 "
            "percent of the issues."
        ),
    },
    {
        "h2": "AI search visibility for {NAME} - what we do differently",
        "body": (
            "AI engines do not rank pages, they extract entities. To be cited in an answer about {NAME} {INDUSTRY_KW}, your "
            "site needs to associate your brand with the city entity, the service entity, and the buyer-intent entity in "
            "the same paragraph patterns that LLM training data rewards. Our content team writes for that pattern explicitly "
            "and we benchmark monthly with Profound and Otterly to see which queries cite us."
        ),
    },
    {
        "h2": "Bilingual content for {NAME} (when the market needs it)",
        "body": (
            "If your {NAME} buyers split between languages (e.g. English + Arabic in Gulf markets, French + Dutch in Brussels, "
            "Spanish + English in Miami), running monolingual content leaves 30 to 50 percent of the demand on the table. "
            "Our content team ships bilingual versions where the market requires it, with proper hreflang and locale-specific "
            "URL paths."
        ),
    },
    {
        "h2": "Pricing and timeline for an {NAME} engagement",
        "body": (
            "Foundation: starts at {COUNTRY_CURRENCY_SYMBOL}1,750/month, 90-day Map Pack target. Growth: from "
            "{COUNTRY_CURRENCY_SYMBOL}4,500/month, multi-neighborhood + organic. Authority: from "
            "{COUNTRY_CURRENCY_SYMBOL}12,500/month, regional dominance. We will tell you which tier fits "
            "before you sign anything, and we publish the same {NAME} pricing publicly so you do not have to negotiate."
        ),
    },
]

INDUSTRY_SECTION_VARIANTS: list[dict] = [
    {
        "h2": "The {NAME} buyer journey we map every program against",
        "body": (
            "Awareness: {PERSONA_1} are searching for educational content like 'what is the best...'. Consideration: "
            "queries shift to 'top {NAME_LOWER} providers' and 'best {NAME_LOWER} for...'. Evaluation: long-tail "
            "comparison and review-driven queries. Decision: branded queries plus consultation requests. We ship content "
            "and schema for each stage so no part of the funnel is leaking."
        ),
    },
    {
        "h2": "Compliance and {REGULATION} considerations for {NAME} marketing",
        "body": (
            "{NAME} content has to satisfy {REGULATION}. Our content workflow embeds compliance review into every brief "
            "so legal does not become the bottleneck. We have shipped content for {NAME} clients in 12+ jurisdictions, "
            "and our review log is auditable so your compliance officer can sign off in hours, not weeks."
        ),
    },
    {
        "h2": "{NAME}-specific schemas and structured data we implement",
        "body": (
            "Generic Organization schema is not enough. We layer on {NAME}-specific structured data: Service, "
            "Offer, AggregateRating, Review, Person (for {PERSONA_1}), and Speakable for AEO. This combination is what "
            "moves rich-result eligibility from 30 percent to 80+ percent on most {NAME} sites within the first quarter."
        ),
    },
    {
        "h2": "Why {NAME} content fails (and how we fix it)",
        "body": (
            "Most {NAME} content fails for one of three reasons: too generic to convert, too compliance-cautious to be "
            "useful, or too sales-y to earn citations. We aim for the middle: useful, specific, compliant. Our editors "
            "have shipped material reviewed by {REGULATION} attorneys with the conversion data to prove the balance is "
            "right."
        ),
    },
    {
        "h2": "Reviews and reputation for {NAME} brands",
        "body": (
            "{PERSONA_1} are unusually sensitive to review velocity and review quality. Below 4.6 stars and your form-fill "
            "rate drops materially. Below 4.4 and it collapses. Our reputation system targets 4.7+ and ships a documented "
            "response framework for the inevitable hostile reviews so they do not tank your aggregate."
        ),
    },
    {
        "h2": "Local SEO + national SEO for {NAME}",
        "body": (
            "Most {NAME} businesses have both a local search opportunity (Map Pack, near-me queries) and a national or "
            "multi-region opportunity (informational queries, comparison queries). Running only one leaves money on the "
            "table. Our program ships both: city-level service-area pages plus deep informational content that ranks "
            "across all your geographies."
        ),
    },
    {
        "h2": "{NAME} pricing benchmarks and what to budget",
        "body": (
            "Based on engagements we have run across {NAME}, the floor for an effective program is about $1,750/month. "
            "That gets you a single-region Map Pack lift plus 4 to 6 long-form articles per quarter. To compete in the "
            "top tier of your category, plan for $4,500 to $12,500/month for 12 to 18 months. The compounding curve "
            "starts to flex around month 9."
        ),
    },
    {
        "h2": "Why we work with {NAME} clients (the criteria)",
        "body": (
            "We turn down about 60 percent of {NAME} prospects because the engagement would not produce ROI inside the "
            "agreed timeline. Our criteria: an offer that converts at 1.5+ percent on cold organic traffic, a revenue "
            "target that justifies the retainer math, a willingness to ship technical fixes within 30 days, and a single "
            "decision-maker on the client side. If you fit those four, we will deliver."
        ),
    },
    {
        "h2": "What changes when {NAME} marketing meets AI search",
        "body": (
            "AI Overviews and ChatGPT Search now intercept a meaningful share of {NAME} queries. To be cited in those "
            "answers, you need entity-level associations between your brand, your offer, and the {NAME} category. We "
            "engineer that with structured FAQ + Speakable + extractable answer paragraphs so the LLM can reason about "
            "your brand as the authoritative source."
        ),
    },
]


COUNTRY_SECTION_VARIANTS: list[dict] = [
    {
        "h2": "How we structure SEO across multiple cities in {NAME}",
        "body": (
            "We do not flatten {NAME} into one keyword set. We tier your target cities into Tier 1 (capital + top "
            "commercial centers), Tier 2 (regional centers), and Tier 3 (long-tail cities). Each tier gets its own content "
            "depth, link investment, and Map Pack execution plan. The compounding curve flexes about 30 percent earlier "
            "when the program runs in this tiered shape."
        ),
    },
    {
        "h2": "Currency, payment, and trust signals for {NAME} buyers",
        "body": (
            "Buyers in {NAME} expect locale-correct currency display, payment methods popular in the region, and trust "
            "badges that the local market recognizes (e.g. consumer-protection seals, local chamber of commerce, regional "
            "industry bodies). Localizing these three signals usually lifts conversion 12 to 25 percent on otherwise "
            "identical pages."
        ),
    },
    {
        "h2": "Multilingual content rules for {NAME}",
        "body": (
            "If your {NAME} buyers operate in more than one language, monolingual content forfeits 30 to 50 percent of "
            "demand. We ship hreflang-correct multilingual content with locale-specific URL paths, properly localized "
            "schema, and language-specific link directories. The biggest mistake we fix on inherited sites is hreflang "
            "implemented incorrectly across 90+ percent of pages."
        ),
    },
    {
        "h2": "{NAME} regulatory and consent considerations",
        "body": (
            "Marketing in {NAME} has its own consent and disclosure norms. Our content workflow bakes in the local consent "
            "banner pattern, the local cookie law, and the local advertising-claim review process. Saves the legal "
            "back-and-forth that usually adds 4 to 8 weeks to launch."
        ),
    },
    {
        "h2": "Seasonal demand patterns we plan against in {NAME}",
        "body": (
            "Most {NAME} categories have a 2 to 3 month period where 30 to 50 percent of annual revenue closes. We plan "
            "the content and link calendar so the pages backing those queries are mature (3+ months indexed, internal "
            "linking complete, GBP optimized) by the time the buyer rush starts. Missing that window costs the equivalent "
            "of one full quarter of organic growth."
        ),
    },
    {
        "h2": "How we expand from one regional cluster to national coverage in {NAME}",
        "body": (
            "Our {NAME} expansion playbook: dominate a single regional cluster (capital + 2 to 3 satellites) for "
            "the first 6 months, then template the same content set for the next regional cluster, then again for the "
            "third. By month 18, you cover 4 to 6 regions with a marginal cost per region that is 30 percent of the cost "
            "of the first cluster."
        ),
    },
    {
        "h2": "Top mistakes we see on inherited {NAME} sites",
        "body": (
            "Hreflang implemented at the page level instead of the cluster level (most common). Region-specific phone "
            "numbers and addresses missing from LocalBusiness schema. Currency hard-coded to USD. Missing rel-alternate "
            "for locale-specific URLs. Country-specific GBP listings unlinked from the multi-region brand. We fix all "
            "five in the first 30 days."
        ),
    },
]


BLOG_SECTION_VARIANTS: list[dict] = [
    {
        "h2": "What changed in 2026 that the older {TOPIC} guides miss",
        "body": (
            "The biggest change is AI Overviews. Google now serves an AI-generated answer above the SERP on more than "
            "half of commercial queries (BrightEdge 2025). That shifts the optimization target from blue-link CTR to "
            "answer-citation share. The older {TOPIC} guides do not address that shift, which is why their tactics now "
            "underperform."
        ),
    },
    {
        "h2": "The 6-step framework we use on every {TOPIC} engagement",
        "body": (
            "Step 1: define the entity graph (brand, offer, target buyer, category, geo). Step 2: audit current SERP and "
            "AI-citation share for the top 50 queries. Step 3: build the content topology (pillar pages, supporting "
            "articles, programmatic templates). Step 4: ship structured FAQ + Speakable + AggregateRating schema. Step "
            "5: build the internal-link graph at edit time, not as an afterthought. Step 6: monitor weekly with Profound "
            "or Otterly to see which queries cite you and which competitors are stealing the answer slot."
        ),
    },
    {
        "h2": "Numbers from our 2025-2026 portfolio",
        "body": (
            "Across our retainer book in 2025 and 2026: average organic-session lift of {AVG_LIFT}% by month 9. AI-citation "
            "share grew from a baseline of 8% to 31% on tracked client queries. Map Pack placement: 71% of local clients "
            "in the top 3 by month 6. The numbers are not promises - they are the rolling median of what we have shipped."
        ),
    },
    {
        "h2": "What we do not recommend for {TOPIC} (and why)",
        "body": (
            "We do not recommend automated programmatic SEO without an editor in the loop. We do not recommend AI-only "
            "content with no human review. We do not recommend ranking-tracking software as the primary KPI. None of "
            "the three correlate well with revenue once a buyer reaches the page."
        ),
    },
    {
        "h2": "How to test whether {TOPIC} is working in 90 days",
        "body": (
            "Set the baseline: GSC click and impression weekly average for the prior 13 weeks, AI-citation share across "
            "the top 50 queries, branded search volume, pipeline attribution. Re-measure at days 30, 60, 90. By day 90 "
            "we expect to see a 15+ percent organic-impression lift and 2+ AI-citation wins on previously uncited queries. "
            "If the program does not hit those, the diagnostic loop kicks in."
        ),
    },
]


RESOURCE_SECTION_VARIANTS: list[dict] = [
    {
        "h2": "What is inside {NAME}",
        "body": (
            "{NAME} is a {LENGTH}-page artifact. Section 1 walks through the framework. Section 2 contains the "
            "fillable templates. Section 3 includes 3 fully-worked examples. Section 4 has the QA checklist. We use "
            "the same artifact on live client engagements."
        ),
    },
    {
        "h2": "Who {NAME} is for",
        "body": (
            "{NAME} is built for {AUDIENCE} who are running their own {TOPIC} and want a battle-tested artifact instead "
            "of starting from a blank page. Senior consultants will recognize the framework. Junior practitioners will "
            "have a structured map to follow. Either way, the artifact saves 10 to 30 hours of cycle time."
        ),
    },
    {
        "h2": "How to use {NAME} (the 30-minute path)",
        "body": (
            "Open the file. Skim the framework on page 1. Fill in the blank fields in your context. Run the QA checklist "
            "on the back page. Ship. The whole thing is designed to be done in a single 30-minute session, not a "
            "multi-week project."
        ),
    },
    {
        "h2": "Why {NAME} is free",
        "body": (
            "Because gating it behind an email form does not increase the number of operators who actually use it. We "
            "would rather have it adopted widely. If you find it useful, send it to a colleague. If you want help "
            "implementing it on your own program, the {BRAND} team is one click away."
        ),
    },
]

TOOL_SECTION_VARIANTS: list[dict] = [
    {
        "h2": "What {NAME} does (and what it does not)",
        "body": (
            "{NAME} runs entirely in your browser. Your input never leaves your device. There is no tracking, no email "
            "gate, no upsell. The tradeoff: it does not call any external API, so the answer is constrained to what "
            "client-side JavaScript can compute. For most jobs that is enough."
        ),
    },
    {
        "h2": "Tips to get a more useful answer from {NAME}",
        "body": (
            "Paste, do not type, when you have a long input. Use the most recent canonical source for what you are "
            "checking. Cross-check the result against a second tool when stakes are high. We treat {NAME} as a fast "
            "first-pass, not as the only authority."
        ),
    },
]


SERVICE_FAQ_VARIANTS: list[dict] = [
    {"q": "How long does it take to see results from {NAME}?", "a": "Most clients see early ranking and indexing movement in 30 to 45 days, traffic lift in 60 to 90 days, and pipeline impact compounding from month 4 onward. {NAME} is not a 7-day game; it is a compounding asset that flexes hardest in months 6 through 18."},
    {"q": "Do you guarantee results for {NAME}?", "a": "Yes. We put a 90-day ROI guarantee in writing: if we miss the agreed milestone, we work free until we hit it. Few firms will sign that clause. We do, because the system we run hits its targets."},
    {"q": "What does {NAME} cost in 2026?", "a": "Foundation tier starts at $1,750/month. Growth is $4,500/month. Authority is $12,500+/month. Pricing depends on competitiveness, content volume, and target market. We will tell you which tier fits your goals before you sign anything."},
    {"q": "How is {NAME} different from in-house SEO?", "a": "In-house teams have product context. We have category context across {COUNTRY_COUNT}+ markets and {INDUSTRY_COUNT}+ industries. We pair best with embedded in-house teams: we run the systems work, your team owns the product narrative."},
    {"q": "Do you work with my CMS / stack?", "a": "Yes. We have shipped {NAME} programs on WordPress, Shopify, Webflow, Magento, custom React, Next.js, Vue, headless CMSes, and old hand-rolled PHP. The CMS rarely matters for SEO outcome; the architectural choices do."},
    {"q": "Can {NAME} be done without modifying our website?", "a": "Partially - off-page work, GBP optimization, and content briefs can be produced without site access. But the highest-ROI work happens on the site itself. Programs without site access typically deliver about 40 percent of the impact of full-access engagements."},
    {"q": "How do you handle reporting and transparency?", "a": "Live Looker Studio dashboard updated daily. Weekly written digest. Monthly executive review. Quarterly strategy reset. You see the same data we do. There is no black-box agency report."},
    {"q": "Do you handle copywriting and editing?", "a": "Yes. We have a specialist team of editors and writers, all human, all experienced in your category before they are assigned. Every piece runs through QA before shipping."},
    {"q": "Will my content sound generic if you write it?", "a": "No. We interview you and your top 3 customers before the first brief. Every piece pulls voice signals from those interviews. Generic agency content is not in our deliverable book."},
    {"q": "What happens if we want to pause or end the engagement?", "a": "30-day written notice on either side, no early-termination fee. We hand off all assets, accesses, and data. We have never had a contested offboarding."},
    {"q": "Do you do work in languages other than English?", "a": "Yes. We deliver in 22 languages including Arabic (RTL), Hebrew (RTL), Chinese, Japanese, Korean, German, French, Spanish, Italian, Dutch, Portuguese, and the Nordic + Slavic clusters. Native-speaker editors review every piece."},
    {"q": "How do you measure AI search visibility for {NAME}?", "a": "We track citations across ChatGPT Search, Perplexity, Claude, Gemini, and Bing Copilot using Profound and Otterly. We benchmark monthly and report the share of cited answers your brand earns inside your top query set."},
    {"q": "What is the typical engagement length?", "a": "Minimum 6 months because the SEO compounding curve does not show up before then. Most clients renew at month 6 and run for 18 to 36 months. The longest active retainer in our book is 5 years."},
    {"q": "Do you train our internal team?", "a": "Yes. Embedded coaching is included in the Authority tier and available as an add-on for Foundation and Growth. We train your in-house team to run the playbook so we eventually work ourselves out of the relationship - or expand into an even more strategic role."},
    {"q": "Can you replace our existing SEO agency?", "a": "Yes, and the transition usually takes 30 days. We forensic-audit the inherited work, salvage the 30 to 50 percent that is keepable, and rebuild the rest. We have done dozens of agency-replacement migrations."},
    {"q": "What if we already rank well organically?", "a": "Then the leverage is in {NAME}'s adjacent disciplines: AI search citations (a different optimization target), conversion rate optimization on the high-traffic pages, internal-link redistribution to lift secondary clusters, and an audit of crawl-budget waste."},
]


CITY_FAQ_VARIANTS: list[dict] = [
    {"q": "How long until we see Map Pack results in {NAME}?", "a": "30 to 60 days for a Foundation engagement, 14 to 30 days for established brands with clean Google Business Profiles. The variance depends on competitor density in your category."},
    {"q": "Do we need a physical address in {NAME} to rank locally?", "a": "Strictly, you need a verifiable address Google can confirm. For service-area businesses without a public storefront, a registered service-area listing works. We help you choose the right model."},
    {"q": "How is local SEO in {NAME} different from {COUNTRY_NAME} as a whole?", "a": "{NAME} has a more competitive Map Pack, different citation directories that actually drive traffic, and buyer language patterns that differ from the national norm. Generic national SEO leaves 40 to 60 percent of the {NAME} opportunity on the table."},
    {"q": "What is the typical monthly budget for {NAME} local SEO?", "a": "{COUNTRY_CURRENCY_SYMBOL}1,750 to {COUNTRY_CURRENCY_SYMBOL}12,500 per month, with most {NAME} clients in the {COUNTRY_CURRENCY_SYMBOL}3,000 to {COUNTRY_CURRENCY_SYMBOL}6,000 range. Custom enterprise plans available."},
    {"q": "Can we run paid ads in {NAME} alongside SEO?", "a": "Yes, and we usually recommend it. Paid + organic together produce a 1.4 to 1.8x lift over either channel run alone. The keyword data crosses over both ways."},
    {"q": "Do you handle Google Business Profile setup and optimization?", "a": "Yes. GBP is one of the highest-ROI assets in any local engagement. We optimize categories, posts, photos, services, FAQ, and reputation response. The work is included in every {NAME} retainer."},
    {"q": "How do you track ROI for {NAME} local marketing?", "a": "GBP-stamped form fills, GBP call tracking, geo-fenced UTM tags, and a pipeline dashboard that attributes closed revenue to landing-page entry. Your CFO can audit any line in the report."},
    {"q": "What if we operate in {NAME} and other cities?", "a": "We tier the cities by commercial density and build a regional priority map. The first wave usually targets your top 3 to 4 cities. We expand from there as the program compounds."},
    {"q": "How do you handle reviews and reputation in {NAME}?", "a": "Automated review-request flow within 24 hours of a positive interaction, sentiment classifier that surfaces high-leverage reviews to the response queue, and a documented framework for responding to hostile reviews so your aggregate rating holds."},
    {"q": "Do you help with multilingual content for {NAME} buyers?", "a": "Yes. We deliver in {LANG_LIST} where the {NAME} market needs it, with proper hreflang and locale-specific URL paths. Native-speaker editors review every piece."},
    {"q": "What does the first 30 days look like for {NAME}?", "a": "Week 1: kickoff, GBP audit, technical audit. Week 2: top-priority technical fixes shipped, GBP optimization complete. Week 3: first 4 to 6 articles in flight, citation build started. Week 4: monthly review and roadmap reset."},
]


INDUSTRY_FAQ_VARIANTS: list[dict] = [
    {"q": "Why do generic SEO agencies struggle with {NAME}?", "a": "Because {NAME} buyer journeys, compliance constraints, and trust-signal expectations are not in their playbook. They ship generic content, miss the {REGULATION} review step, and underweight the schemas that move the needle for your category."},
    {"q": "How long does {NAME} SEO take to produce ROI?", "a": "60 to 90 days for early ranking and indexing wins, 4 to 6 months for pipeline impact, 9 to 18 months for the compounding curve to flex. {NAME} is a long-game asset, not a 7-day campaign."},
    {"q": "What does an effective {NAME} content brief look like?", "a": "Compliance-reviewed claims, persona-targeted voice, structured FAQ + Speakable schema, internal-link plan to 4 to 6 related pages, and an extractable answer paragraph for AI engines. Generic briefs miss 4 of those 5."},
    {"q": "Do you handle compliance review for {NAME} marketing?", "a": "Yes. {REGULATION} review is built into every brief. Our editors have shipped material reviewed by industry attorneys with the conversion data to prove the balance is right."},
    {"q": "How do you measure the buying journey for {NAME}?", "a": "Each landing page is mapped to a UTM-tagged conversion path. We attribute pipeline at the page level so you can see exactly which content is producing revenue and which is just producing traffic."},
    {"q": "What is the typical {NAME} engagement length?", "a": "Most {NAME} retainers run 12 to 24 months. The compounding curve flexes hardest around month 9 to month 12, so cutting the program before then forfeits the steepest part of the return."},
    {"q": "Can you work with our internal compliance or legal team?", "a": "Yes. We have shipped {NAME} content reviewed by in-house counsel at 12+ regulated firms. Our review log is auditable and we adapt to your house style."},
    {"q": "How do you balance compliance with conversion in {NAME} content?", "a": "We aim for the middle: useful, specific, compliant. Material that is too generic does not convert. Material that is too sales-y does not survive review. The sweet spot is documented in our editor playbook."},
    {"q": "Do you work with mid-market {NAME} firms or only enterprise?", "a": "Both. Foundation tier ($1,750/month) is built for early-stage and mid-market {NAME} firms. Authority tier ($12,500+) is built for national and multinational {NAME} brands. The methodology is the same; the depth and pace differ."},
    {"q": "How do reviews and reputation work for {NAME} clients?", "a": "Reputation is one of the top 3 ranking factors for {NAME} buyers. Our system targets 4.7+ stars with documented response framework for hostile reviews. We have lifted aggregate ratings from 4.3 to 4.7+ on multiple {NAME} clients."},
]


COUNTRY_FAQ_VARIANTS: list[dict] = [
    {"q": "Do you have local SEO experience inside {NAME}?", "a": "Yes. We have run engagements across {NAME} since 2020 and have shipped content, GBP optimization, citation builds, and link campaigns in {LANG_LIST}. Native-speaker editors review every piece in-market."},
    {"q": "What is the typical {NAME} engagement budget?", "a": "Foundation $1,750/month for single-region targeting. Growth $4,500/month for multi-region campaigns. Authority $12,500+/month for national or multinational coverage. The right tier depends on category competitiveness and revenue target."},
    {"q": "How do you handle {NAME} payment methods and currency?", "a": "Pages display {COUNTRY_CURRENCY} pricing locally, payment-method icons match what buyers in {NAME} expect, and trust badges localize to the {NAME} consumer-protection seals where relevant. Localizing these signals lifts conversion 12 to 25 percent."},
    {"q": "Do you have {NAME} staff or are you remote?", "a": "We are a hybrid team with leads on the ground in major regions. The advantage of remote-first is that we hire the best operator regardless of location. The advantage of in-region leads is local language and local context. We get both."},
    {"q": "How do you handle {NAME} regulatory and consent requirements?", "a": "Our content workflow bakes in the local consent banner, the local cookie law, and the local advertising-claim review process. Saves the legal back-and-forth that usually adds 4 to 8 weeks to launch."},
    {"q": "Do you ship multilingual content for {NAME}?", "a": "Yes. We deliver in {LANG_LIST}, with proper hreflang, locale-specific URL paths, and locale-correct schema. Native-speaker editors handle every piece."},
    {"q": "How do you expand from one {NAME} region to national coverage?", "a": "We dominate a single regional cluster (capital + 2 to 3 satellites) for the first 6 months, then template the same content set for the next regional cluster. By month 18 you cover 4 to 6 regions with marginal cost per region around 30 percent of the first cluster."},
    {"q": "What seasonal patterns matter for {NAME}?", "a": "Most categories in {NAME} have a 2 to 3 month period where 30 to 50 percent of annual revenue closes. We plan the content and link calendar so the supporting pages are mature (3+ months indexed, internal linking complete) by the time the buyer rush starts."},
]

BLOG_FAQ_VARIANTS: list[dict] = [
    {"q": "What is the source data behind this guide?", "a": "First-party data from our 2025 and 2026 client engagements, plus published industry data from BrightEdge, BrightLocal, Search Engine Land, and Google's own developer documentation. Where a number is cited, the source is footnoted in the source data file."},
    {"q": "How often is this guide updated?", "a": "We re-review every quarter. When a tactic stops working or a new tactic ships, we update the article and bump the dateModified. The version log is at the bottom of the post."},
    {"q": "Is this guide written by a human or by AI?", "a": "Human-written, AI-assisted on the research phase. Every paragraph is reviewed by a senior editor with category experience. We do not ship AI-only content because it does not survive expert review."},
    {"q": "Can I implement these tactics without an agency?", "a": "Yes. Most of the framework is operationalizable internally with a senior SEO or marketing engineer. The bottleneck is usually content velocity, not knowledge. If the team has 30 hours per week of execution time, the program can run in-house."},
    {"q": "Where can I get help implementing this for our brand?", "a": "Free 30-minute consultation: book at the contact page. Or click into the Free Audit at the top of this page and we will respond within 24 hours."},
]

RESOURCE_FAQ_VARIANTS: list[dict] = [
    {"q": "Is {NAME} actually free, or is it gated?", "a": "Actually free. No email gate, no signup, no upsell. We made it free because gating it behind a form does not increase adoption."},
    {"q": "Can I share or modify {NAME}?", "a": "Yes. Use it on your own client engagements, modify it for your context, and share it with colleagues. We only ask that you do not strip the {BRAND} attribution."},
    {"q": "How does {NAME} compare to a paid competitor template?", "a": "Most paid competitor templates were written by people who have never run a real engagement. {NAME} comes from running 100+ live programs across 22 languages and 78 countries. The template is operator-grade."},
    {"q": "Do I need any tools to use {NAME}?", "a": "Most of the workflow runs in a spreadsheet. A few sections benefit from Ahrefs or Screaming Frog access. We note where each tool would help and where the no-tool version still works."},
]

TOOL_FAQ_VARIANTS: list[dict] = [
    {"q": "Is {NAME} actually free, with no signup?", "a": "Yes. Runs entirely in your browser. We do not log inputs and we do not call an external server. The tool exists because we use it ourselves and figured others would benefit."},
    {"q": "Why does {NAME} sometimes give a different answer from another online tool?", "a": "Tools differ in tokenizer, parser, or rounding logic. We document our calculation methodology at the bottom of the tool. Cross-check against a second tool when the stakes are high."},
    {"q": "Can I embed {NAME} on my own site?", "a": "Not currently. If you want a white-label version for your team or clients, contact us and we can scope it."},
]


# === Builders =========================================================
def _short_currency_symbol(currency: str) -> str:
    return {
        "USD": "$", "EUR": "EUR ", "GBP": "GBP ", "AED": "AED ", "SAR": "SAR ",
        "PKR": "PKR ", "INR": "INR ", "JPY": "JPY ", "CNY": "CNY ", "KRW": "KRW ",
        "ILS": "ILS ", "TRY": "TRY ", "EGP": "EGP ", "QAR": "QAR ", "KWD": "KWD ",
        "BHD": "BHD ", "OMR": "OMR ", "ZAR": "ZAR ", "BRL": "BRL ", "MXN": "MXN ",
        "ARS": "ARS ", "CLP": "CLP ", "PEN": "PEN ", "COP": "COP ", "AUD": "AUD ",
        "NZD": "NZD ", "CAD": "CAD ", "CHF": "CHF ", "SEK": "SEK ", "NOK": "NOK ",
        "DKK": "DKK ", "PLN": "PLN ", "CZK": "CZK ", "HUF": "HUF ", "RON": "RON ",
        "LBP": "LBP ", "JOD": "JOD ", "MAD": "MAD ", "TND": "TND ", "DZD": "DZD ",
        "SGD": "SGD ", "HKD": "HKD ", "TWD": "TWD ", "THB": "THB ", "MYR": "MYR ",
        "IDR": "IDR ", "PHP": "PHP ", "VND": "VND ",
    }.get(currency, currency + " ") if currency else "$"


def _format_template(s: str, ctx: dict) -> str:
    out = s
    for k, v in ctx.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def _last_modified_for(slug: str) -> str:
    """Deterministic-but-realistic recent dateModified per slug."""
    rng = rng_for(slug, "lastmod")
    today = date.today()
    days_back = rng.randint(1, 90)
    return (today - timedelta(days=days_back)).isoformat()


def build_unique_for_service(item: dict, brand: dict, country_count: int = 78, industry_count: int = 230) -> dict:
    slug = item["slug"]
    name = item.get("name") or slug.replace("-", " ").title()

    tools = SERVICE_TOOLS.get(slug, SERVICE_TOOLS["default"])
    tools_primary = ", ".join(tools[:3])
    tools_secondary = ", ".join(tools[3:6]) if len(tools) >= 6 else ", ".join(tools[3:])
    tools_all = ", ".join(tools)

    sample_cities = ["Dubai", "London", "New York", "Singapore", "Berlin", "Tokyo"]
    sample_city = pick(slug, "city", sample_cities)
    sample_city_2 = pick(slug, "city2", [c for c in sample_cities if c != sample_city])

    ctx = {
        "NAME": name,
        "NAME_LOWER": name.lower(),
        "BRAND": brand.get("shortName", "Shahab Abbasi"),
        "TOOLS": tools_all,
        "TOOLS_PRIMARY": tools_primary,
        "TOOLS_SECONDARY": tools_secondary,
        "Y1_TRAFFIC": f"{rng_for(slug, 'y1').randint(2, 8)},{rng_for(slug, 'y1b').randint(100, 999)}",
        "Y2_TRAFFIC": f"{rng_for(slug, 'y2').randint(8, 22)},{rng_for(slug, 'y2b').randint(100, 999)}",
        "Y3_TRAFFIC": f"{rng_for(slug, 'y3').randint(22, 60)},{rng_for(slug, 'y3b').randint(100, 999)}",
        "CWV_LCP": METRIC_TARGETS["lcp"],
        "CWV_INP": METRIC_TARGETS["inp"],
        "CWV_CLS": METRIC_TARGETS["cls"],
        "CRAWL_BUDGET": METRIC_TARGETS["crawl_budget"],
        "INTERNAL_LINKS": METRIC_TARGETS["internal_links"],
        "AI_CITATIONS": METRIC_TARGETS["ai_citations"],
        "COUNTRY_COUNT": str(country_count),
        "INDUSTRY_COUNT": str(industry_count),
        "SAMPLE_CITY": sample_city,
        "SAMPLE_CITY_2": sample_city_2,
        "COUNTRY_NAME": pick(slug, "country", ["the UAE", "Pakistan", "the United States", "the United Kingdom", "Germany", "Singapore"]),
    }

    intro_a = _format_template(pick(slug, "intro", SERVICE_INTRO_TEMPLATES), ctx)
    intro_b = _format_template(pick(slug, "intro2", SERVICE_INTRO_TEMPLATES_2), ctx)
    intro = intro_a + " " + intro_b
    sections_chosen = pick_n(slug, "sec", SERVICE_SECTION_VARIANTS, 5)
    sections = [{"h2": _format_template(s["h2"], ctx), "body": _format_template(s["body"], ctx)} for s in sections_chosen]
    faqs_chosen = pick_n(slug, "faq", SERVICE_FAQ_VARIANTS, 8)
    faqs = [{"q": _format_template(f["q"], ctx), "a": _format_template(f["a"], ctx)} for f in faqs_chosen]

    return {
        "intro_html": intro,
        "sections": sections,
        "faqs": faqs,
        "tools_used": tools,
        "lastmod": _last_modified_for(slug),
        "page_type": "service",
    }


def build_unique_for_industry(item: dict, brand: dict) -> dict:
    slug = item["slug"]
    name = item.get("name") or slug.replace("-", " ").title()
    parent = item.get("parentCategory", "professional-services")
    regulations = REGULATIONS.get(parent, REGULATIONS["professional-services"])
    personas = PERSONAS.get(parent, PERSONAS["default"])

    ctx = {
        "NAME": name,
        "NAME_LOWER": name.lower(),
        "BRAND": brand.get("shortName", "Shahab Abbasi"),
        "REGULATION": pick(slug, "reg", regulations),
        "PERSONA_1": personas[0],
        "PERSONA_2": personas[1] if len(personas) > 1 else personas[0],
        "PERSONA": personas[0],
    }

    intro_a = _format_template(pick(slug, "intro", INDUSTRY_INTRO_TEMPLATES), ctx)
    intro_b = _format_template(pick(slug, "intro2", INDUSTRY_INTRO_TEMPLATES_2), ctx)
    intro = intro_a + " " + intro_b
    sections_chosen = pick_n(slug, "sec", INDUSTRY_SECTION_VARIANTS, 5)
    sections = [{"h2": _format_template(s["h2"], ctx), "body": _format_template(s["body"], ctx)} for s in sections_chosen]
    faqs_chosen = pick_n(slug, "faq", INDUSTRY_FAQ_VARIANTS, 7)
    faqs = [{"q": _format_template(f["q"], ctx), "a": _format_template(f["a"], ctx)} for f in faqs_chosen]

    return {
        "intro_html": intro,
        "sections": sections,
        "faqs": faqs,
        "regulations": regulations,
        "personas": personas,
        "lastmod": _last_modified_for(slug),
        "page_type": "industry",
    }


def build_unique_for_city(item: dict, country: dict, brand: dict, industries: list | None = None) -> dict:
    slug = item["slug"]
    name = item.get("name") or slug.replace("seo-services-", "").replace("-", " ").title()
    cc = country.get("code") or country.get("countryCode") or "default"
    landmarks = COUNTRY_LANDMARKS.get(cc, ["the central business district", "the waterfront", "the old town"])
    chosen_landmarks = pick_n(slug, "land", landmarks, 3)
    industry_kw = "service"
    if industries:
        industry_kw = pick(slug, "ikw", [i.get("name", "service").lower().replace(" seo", "") for i in industries[:10]])
    currency = country.get("currency", "USD")

    cc_to_lang = {"AE": "Arabic", "SA": "Arabic", "QA": "Arabic", "LB": "Arabic", "MA": "Arabic", "EG": "Arabic", "JO": "Arabic", "KW": "Arabic", "BH": "Arabic", "OM": "Arabic", "DZ": "Arabic", "TN": "Arabic", "DE": "German", "FR": "French", "ES": "Spanish", "IT": "Italian", "PT": "Portuguese", "BR": "Portuguese", "NL": "Dutch", "BE": "Dutch and French", "DK": "Danish", "SE": "Swedish", "NO": "Norwegian", "FI": "Finnish", "PL": "Polish", "CZ": "Czech", "HU": "Hungarian", "RO": "Romanian", "GR": "Greek", "TR": "Turkish", "JP": "Japanese", "KR": "Korean", "CN": "Chinese", "TW": "Chinese", "IL": "Hebrew", "PK": "Urdu and English", "IN": "Hindi and English"}
    cc_to_tz = {"AE": "UTC+4", "SA": "UTC+3", "QA": "UTC+3", "LB": "UTC+2", "PK": "UTC+5", "IN": "UTC+5:30", "DE": "UTC+1", "FR": "UTC+1", "ES": "UTC+1", "IT": "UTC+1", "GB": "UTC+0", "US": "UTC-5 to UTC-8 depending on region", "JP": "UTC+9", "KR": "UTC+9", "CN": "UTC+8", "AU": "UTC+10", "SG": "UTC+8", "BR": "UTC-3", "TR": "UTC+3", "EG": "UTC+2", "ZA": "UTC+2", "IL": "UTC+2", "RU": "UTC+3"}
    cc_to_payments = {"AE": "Mada, Apple Pay, Visa/Mastercard, and bank transfers", "SA": "Mada, STC Pay, and Visa/Mastercard", "PK": "Easypaisa, JazzCash, Visa/Mastercard, and IBFT bank transfers", "IN": "UPI, Paytm, RuPay, and Visa/Mastercard", "EG": "Fawry, Vodafone Cash, and Visa/Mastercard", "BR": "Pix, Boleto, and Visa/Mastercard", "DE": "SEPA, Klarna, PayPal, and Visa/Mastercard", "JP": "credit cards, conbini cash, and PayPay", "KR": "KakaoPay, NaverPay, and Visa/Mastercard", "GB": "Visa/Mastercard, Apple Pay, and bank transfers"}
    ctx = {
        "NAME": name,
        "NAME_LOWER": name.lower(),
        "COUNTRY_NAME": country.get("name", ""),
        "COUNTRY_CURRENCY": currency,
        "COUNTRY_CURRENCY_SYMBOL": _short_currency_symbol(currency),
        "INDUSTRY_KW": industry_kw,
        "INDUSTRY_HINT": industry_kw,
        "LANDMARK_1": chosen_landmarks[0] if chosen_landmarks else "the central business district",
        "LANDMARK_2": chosen_landmarks[1] if len(chosen_landmarks) > 1 else "the waterfront",
        "LANDMARK_3": chosen_landmarks[2] if len(chosen_landmarks) > 2 else "the old town",
        "NEIGHBORHOOD_1": chosen_landmarks[0] if chosen_landmarks else "the city centre",
        "BRAND": brand.get("shortName", "Shahab Abbasi"),
        "LANG_LIST": "Arabic, English, French" if cc in {"AE","SA","QA","LB","MA"} else "English plus the local language(s)",
        "LOCAL_LANGUAGE": cc_to_lang.get(cc, "the primary local language"),
        "TIMEZONE": cc_to_tz.get(cc, "the local timezone"),
        "LOCAL_PAYMENT_METHODS": cc_to_payments.get(cc, "Visa/Mastercard, local digital wallets, and bank transfers"),
        "DOMINANT_REVIEW_SITE": pick(slug, "review_site", ["Google reviews", "Trustpilot", "Yelp"]),
        "CURRENCY": currency,
    }

    intro_a = _format_template(pick(slug, "intro", CITY_INTRO_TEMPLATES), ctx)
    intro_b = _format_template(pick(slug, "intro2", CITY_INTRO_TEMPLATES_2), ctx)
    intro = intro_a + " " + intro_b
    sections_chosen = pick_n(slug, "sec", CITY_SECTION_VARIANTS, 5)
    sections = [{"h2": _format_template(s["h2"], ctx), "body": _format_template(s["body"], ctx)} for s in sections_chosen]
    faqs_chosen = pick_n(slug, "faq", CITY_FAQ_VARIANTS, 7)
    faqs = [{"q": _format_template(f["q"], ctx), "a": _format_template(f["a"], ctx)} for f in faqs_chosen]

    return {
        "intro_html": intro,
        "sections": sections,
        "faqs": faqs,
        "landmarks": chosen_landmarks,
        "lastmod": _last_modified_for(slug),
        "page_type": "city",
    }


def build_unique_for_country(item: dict, brand: dict) -> dict:
    slug = item["slug"]
    name = item.get("name") or slug.replace("-", " ").title()
    currency = item.get("currency", "USD")

    ctx = {
        "NAME": name,
        "NAME_LOWER": name.lower(),
        "COUNTRY_CURRENCY": currency,
        "COUNTRY_CURRENCY_SYMBOL": _short_currency_symbol(currency),
        "BRAND": brand.get("shortName", "Shahab Abbasi"),
        "LANG_LIST": "the primary local language(s)",
    }

    intro_a = _format_template(pick(slug, "intro", COUNTRY_INTRO_TEMPLATES), ctx)
    intro_b = _format_template(pick(slug, "intro2", COUNTRY_INTRO_TEMPLATES_2), ctx)
    intro = intro_a + " " + intro_b
    sections_chosen = pick_n(slug, "sec", COUNTRY_SECTION_VARIANTS, 5)
    sections = [{"h2": _format_template(s["h2"], ctx), "body": _format_template(s["body"], ctx)} for s in sections_chosen]
    faqs_chosen = pick_n(slug, "faq", COUNTRY_FAQ_VARIANTS, 6)
    faqs = [{"q": _format_template(f["q"], ctx), "a": _format_template(f["a"], ctx)} for f in faqs_chosen]

    return {
        "intro_html": intro,
        "sections": sections,
        "faqs": faqs,
        "lastmod": _last_modified_for(slug),
        "page_type": "country",
    }


def build_unique_for_blog(item: dict, brand: dict) -> dict:
    slug = item["slug"]
    title = item.get("title") or item.get("name") or slug
    topic = item.get("primaryKeyword") or title.lower()

    ctx = {
        "TITLE": title,
        "TOPIC": topic,
        "BRAND": brand.get("shortName", "Shahab Abbasi"),
        "AUDIENCE": pick(slug, "aud", ["operators", "in-house SEO leads", "marketing directors", "founders", "growth leads"]),
        "AVG_LIFT": str(rng_for(slug, "lift").randint(38, 78)),
    }

    intro_a = _format_template(pick(slug, "intro", BLOG_INTRO_TEMPLATES), ctx)
    intro_b = _format_template(pick(slug, "intro2", BLOG_INTRO_TEMPLATES_2), ctx)
    intro = intro_a + " " + intro_b
    sections_chosen = pick_n(slug, "sec", BLOG_SECTION_VARIANTS, 5)
    sections = [{"h2": _format_template(s["h2"], ctx), "body": _format_template(s["body"], ctx)} for s in sections_chosen]
    faqs_chosen = pick_n(slug, "faq", BLOG_FAQ_VARIANTS, 4)
    faqs = [{"q": _format_template(f["q"], ctx), "a": _format_template(f["a"], ctx)} for f in faqs_chosen]

    return {
        "intro_html": intro,
        "sections": sections,
        "faqs": faqs,
        "lastmod": _last_modified_for(slug),
        "word_count": rng_for(slug, "words").randint(1800, 2400),
        "reading_time_minutes": rng_for(slug, "read").randint(8, 14),
        "page_type": "blog",
    }


def build_unique_for_resource(item: dict, brand: dict) -> dict:
    slug = item["slug"]
    name = item.get("name") or item.get("title") or slug

    ctx = {
        "NAME": name,
        "TOPIC": item.get("primaryKeyword") or name.lower(),
        "BRAND": brand.get("shortName", "Shahab Abbasi"),
        "AUDIENCE": pick(slug, "aud", ["operators", "consultants", "in-house SEO leads", "growth leads"]),
        "LENGTH": str(rng_for(slug, "len").randint(8, 24)),
    }

    intro_a = _format_template(pick(slug, "intro", RESOURCE_INTRO_TEMPLATES), ctx)
    intro_b = _format_template(pick(slug, "intro2", RESOURCE_INTRO_TEMPLATES_2), ctx)
    intro = intro_a + " " + intro_b
    sections_chosen = pick_n(slug, "sec", RESOURCE_SECTION_VARIANTS, 4)
    sections = [{"h2": _format_template(s["h2"], ctx), "body": _format_template(s["body"], ctx)} for s in sections_chosen]
    faqs_chosen = pick_n(slug, "faq", RESOURCE_FAQ_VARIANTS, 4)
    faqs = [{"q": _format_template(f["q"], ctx), "a": _format_template(f["a"], ctx)} for f in faqs_chosen]

    return {
        "intro_html": intro,
        "sections": sections,
        "faqs": faqs,
        "lastmod": _last_modified_for(slug),
        "page_type": "resource",
    }


def build_unique_for_tool(item: dict, brand: dict) -> dict:
    slug = item["slug"]
    name = item.get("name") or item.get("title") or slug

    ctx = {
        "NAME": name,
        "BRAND": brand.get("shortName", "Shahab Abbasi"),
        "AUDIENCE": pick(slug, "aud", ["SEOs", "marketers", "writers", "operators", "developers"]),
    }

    intro_a = _format_template(pick(slug, "intro", TOOL_INTRO_TEMPLATES), ctx)
    intro_b = _format_template(pick(slug, "intro2", TOOL_INTRO_TEMPLATES_2), ctx)
    intro = intro_a + " " + intro_b
    sections_chosen = pick_n(slug, "sec", TOOL_SECTION_VARIANTS, 2)
    sections = [{"h2": _format_template(s["h2"], ctx), "body": _format_template(s["body"], ctx)} for s in sections_chosen]
    faqs_chosen = pick_n(slug, "faq", TOOL_FAQ_VARIANTS, 3)
    faqs = [{"q": _format_template(f["q"], ctx), "a": _format_template(f["a"], ctx)} for f in faqs_chosen]

    return {
        "intro_html": intro,
        "sections": sections,
        "faqs": faqs,
        "lastmod": _last_modified_for(slug),
        "page_type": "tool",
    }
