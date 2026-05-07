"""Populate master-data.json with the long-tail data (industries, tools, countries,
cities, blog topics, resources) so it is a complete starter the user can edit.

Run from repo root: ``python scripts/populate_data.py``.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "master-data.json"


def slugify(name: str) -> str:
    s = name.lower()
    for old, new in [("&", "and"), ("/", "-"), (" - ", "-")]:
        s = s.replace(old, new)
    # Strip punctuation that is invalid or noisy in URLs
    for ch in [":", ";", ",", ".", "?", "!", "'", '"', "(", ")", "[", "]", "{", "}", "@", "#", "%", "*"]:
        s = s.replace(ch, "")
    s = s.replace(" ", "-")
    # Collapse double-hyphens
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


# ---------------------------------------------------------------------------
# 150+ industries (rough grouping per Section 4 of master prompt)
# ---------------------------------------------------------------------------

INDUSTRY_SEED: list[tuple[str, str]] = [
    # Healthcare & Medical
    ("Dentists", "healthcare-medical"),
    ("Orthodontists", "healthcare-medical"),
    ("Cosmetic Surgeons", "healthcare-medical"),
    ("Dermatologists", "healthcare-medical"),
    ("Chiropractors", "healthcare-medical"),
    ("Physical Therapists", "healthcare-medical"),
    ("Mental Health Clinics", "healthcare-medical"),
    ("Veterinary Clinics", "healthcare-medical"),
    ("Hospitals", "healthcare-medical"),
    ("Medical Spas", "healthcare-medical"),
    ("Optometrists", "healthcare-medical"),
    ("Pediatricians", "healthcare-medical"),
    ("Plastic Surgeons", "healthcare-medical"),
    ("IVF Clinics", "healthcare-medical"),
    ("Telemedicine", "healthcare-medical"),
    # Legal & Law
    ("Personal Injury Lawyers", "legal-law"),
    ("Criminal Defense Lawyers", "legal-law"),
    ("Family Law Attorneys", "legal-law"),
    ("Immigration Attorneys", "legal-law"),
    ("Corporate Law Firms", "legal-law"),
    ("Real Estate Attorneys", "legal-law"),
    ("Estate Planning Attorneys", "legal-law"),
    ("Bankruptcy Lawyers", "legal-law"),
    ("Employment Lawyers", "legal-law"),
    ("Tax Attorneys", "legal-law"),
    ("Divorce Lawyers", "legal-law"),
    ("Workers Compensation Lawyers", "legal-law"),
    # Home Services
    ("Roofing Contractors", "home-services"),
    ("HVAC Contractors", "home-services"),
    ("Plumbers", "home-services"),
    ("Electricians", "home-services"),
    ("Painters", "home-services"),
    ("Landscapers", "home-services"),
    ("Pest Control", "home-services"),
    ("Cleaning Services", "home-services"),
    ("Pool Builders", "home-services"),
    ("General Contractors", "home-services"),
    ("Solar Installers", "home-services"),
    ("Interior Designers", "home-services"),
    ("Carpet Cleaners", "home-services"),
    ("Garage Door Companies", "home-services"),
    ("Locksmiths", "home-services"),
    # Ecommerce & Retail
    ("Shopify Stores", "ecommerce-retail"),
    ("WooCommerce Stores", "ecommerce-retail"),
    ("Magento Stores", "ecommerce-retail"),
    ("BigCommerce Stores", "ecommerce-retail"),
    ("Fashion Brands", "ecommerce-retail"),
    ("Beauty Brands", "ecommerce-retail"),
    ("Jewelry Brands", "ecommerce-retail"),
    ("Furniture Stores", "ecommerce-retail"),
    ("Pet Supplies", "ecommerce-retail"),
    ("Electronics Stores", "ecommerce-retail"),
    ("Sporting Goods", "ecommerce-retail"),
    ("Subscription Boxes", "ecommerce-retail"),
    ("Marketplaces", "ecommerce-retail"),
    # Real Estate
    ("Real Estate Agents", "real-estate"),
    ("Real Estate Brokerages", "real-estate"),
    ("Property Managers", "real-estate"),
    ("Mortgage Brokers", "real-estate"),
    ("Real Estate Developers", "real-estate"),
    ("Vacation Rentals", "real-estate"),
    ("Commercial Real Estate", "real-estate"),
    ("Real Estate Investors", "real-estate"),
    # SaaS & Tech
    ("B2B SaaS", "saas-tech"),
    ("FinTech Startups", "saas-tech"),
    ("HealthTech Startups", "saas-tech"),
    ("EdTech Startups", "saas-tech"),
    ("Cybersecurity Companies", "saas-tech"),
    ("AI Companies", "saas-tech"),
    ("Mobile App Companies", "saas-tech"),
    ("DevTools", "saas-tech"),
    ("Web3 & Crypto", "saas-tech"),
    ("MarTech Platforms", "saas-tech"),
    ("HRTech Platforms", "saas-tech"),
    ("LegalTech Platforms", "saas-tech"),
    # Finance
    ("Financial Advisors", "finance"),
    ("Accounting Firms", "finance"),
    ("Insurance Brokers", "finance"),
    ("Wealth Managers", "finance"),
    ("Banking Services", "finance"),
    ("Investment Firms", "finance"),
    ("Crypto Exchanges", "finance"),
    ("Loan Companies", "finance"),
    ("Tax Preparers", "finance"),
    # Education
    ("Online Course Creators", "education"),
    ("Universities", "education"),
    ("Bootcamps", "education"),
    ("Tutoring Services", "education"),
    ("K-12 Schools", "education"),
    ("Test Prep Companies", "education"),
    ("Language Schools", "education"),
    ("Vocational Training", "education"),
    # Hospitality
    ("Hotels", "hospitality"),
    ("Restaurants", "hospitality"),
    ("Cafes", "hospitality"),
    ("Bars and Nightclubs", "hospitality"),
    ("Travel Agencies", "hospitality"),
    ("Tour Operators", "hospitality"),
    ("Resorts", "hospitality"),
    ("Catering Services", "hospitality"),
    ("Event Planners", "hospitality"),
    # Automotive
    ("Auto Dealerships", "automotive"),
    ("Auto Repair Shops", "automotive"),
    ("Auto Body Shops", "automotive"),
    ("Tire Shops", "automotive"),
    ("Car Detailing", "automotive"),
    ("Motorcycle Dealers", "automotive"),
    ("Auto Parts Retailers", "automotive"),
    ("Car Rental Companies", "automotive"),
    ("Trucking Companies", "automotive"),
    # Manufacturing
    ("Industrial Manufacturers", "manufacturing"),
    ("Custom Fabricators", "manufacturing"),
    ("Aerospace Suppliers", "manufacturing"),
    ("Plastics Manufacturers", "manufacturing"),
    ("Metal Fabricators", "manufacturing"),
    ("Food and Beverage Manufacturers", "manufacturing"),
    ("Chemical Manufacturers", "manufacturing"),
    ("Packaging Manufacturers", "manufacturing"),
    # Non-profit
    ("Non-profit Organizations", "non-profit"),
    ("Charities", "non-profit"),
    ("Foundations", "non-profit"),
    ("NGOs", "non-profit"),
    ("Religious Organizations", "non-profit"),
    ("Community Associations", "non-profit"),
    # Misc / extra to reach 150
    ("Marketing Agencies", "saas-tech"),
    ("Coaches and Consultants", "saas-tech"),
    ("Photographers", "home-services"),
    ("Videographers", "home-services"),
    ("Wedding Planners", "hospitality"),
    ("Florists", "hospitality"),
    ("Bakeries", "hospitality"),
    ("Gyms and Fitness Studios", "healthcare-medical"),
    ("Yoga Studios", "healthcare-medical"),
    ("Med Spas", "healthcare-medical"),
    ("Hair Salons", "home-services"),
    ("Barbershops", "home-services"),
    ("Nail Salons", "home-services"),
    ("Tattoo Studios", "home-services"),
    ("Pet Groomers", "home-services"),
    ("Daycare Centers", "education"),
    ("Sleep Coaches", "healthcare-medical"),
    ("Nutritionists", "healthcare-medical"),
    ("Personal Trainers", "healthcare-medical"),
    ("Doulas and Midwives", "healthcare-medical"),
    ("Cannabis Dispensaries", "ecommerce-retail"),
    ("CBD Brands", "ecommerce-retail"),
    ("Wineries", "hospitality"),
    ("Breweries", "hospitality"),
    ("Distilleries", "hospitality"),
    ("Boutique Hotels", "hospitality"),
    ("Glamping Resorts", "hospitality"),
    ("Co-working Spaces", "real-estate"),
    ("Self-Storage Facilities", "real-estate"),
    ("Funeral Homes", "non-profit"),
    ("Florist E-commerce", "ecommerce-retail"),
    ("Online Therapy", "healthcare-medical"),
    ("Online Pharmacies", "healthcare-medical"),
    ("Mortgage Lenders", "finance"),
    ("Forex Brokers", "finance"),
    ("Crypto Wallets", "saas-tech"),
    ("NFT Marketplaces", "saas-tech"),
    ("Logistics Companies", "manufacturing"),
    ("Freight Forwarders", "manufacturing"),
    ("3PL Providers", "manufacturing"),
]


def build_industries() -> list[dict]:
    out = []
    for name, cat in INDUSTRY_SEED:
        slug = slugify(name)
        out.append(
            {
                "slug": slug,
                "name": name,
                "primaryKeyword": f"SEO for {name.lower()}",
                "lsiKeywords": [
                    f"{name.lower()} marketing",
                    f"{name.lower()} digital marketing",
                    f"{name.lower()} lead generation",
                    f"{name.lower()} PPC",
                    f"{name.lower()} local SEO",
                ],
                "shortDescription": (
                    f"Industry-specific SEO and growth marketing built for {name.lower()}, "
                    "with playbooks, schema, and conversion tactics that move the needle."
                ),
                "heroImagePrompt": f"professional {name.lower()} office or workspace, modern, dark navy and electric blue accents",
                "parentCategory": cat,
            }
        )
    return out


# ---------------------------------------------------------------------------
# 85+ tools across 12 categories
# ---------------------------------------------------------------------------

TOOL_SEED: list[tuple[str, str]] = [
    # Keyword Tools
    ("Keyword Density Analyzer", "keyword-tools"),
    ("Keyword Difficulty Estimator", "keyword-tools"),
    ("Long-Tail Keyword Generator", "keyword-tools"),
    ("Search Intent Classifier", "keyword-tools"),
    ("LSI Keyword Generator", "keyword-tools"),
    ("PAA Question Extractor", "keyword-tools"),
    ("Keyword Cluster Builder", "keyword-tools"),
    # Technical SEO Tools
    ("Robots.txt Tester", "technical-seo-tools"),
    ("XML Sitemap Generator", "technical-seo-tools"),
    ("Hreflang Tag Generator", "technical-seo-tools"),
    ("Canonical Tag Checker", "technical-seo-tools"),
    ("HTTP Header Inspector", "technical-seo-tools"),
    ("Redirect Chain Checker", "technical-seo-tools"),
    ("Mobile-Friendly Tester", "technical-seo-tools"),
    ("Core Web Vitals Checker", "technical-seo-tools"),
    ("Crawl Budget Estimator", "technical-seo-tools"),
    # Content Tools
    ("Word Counter", "content-tools"),
    ("Readability Score Calculator", "content-tools"),
    ("Content Gap Analyzer", "content-tools"),
    ("Meta Tag Generator", "meta-tools"),
    ("Title Tag Optimizer", "meta-tools"),
    ("Meta Description Generator", "meta-tools"),
    ("OpenGraph Tag Generator", "meta-tools"),
    ("Twitter Card Generator", "meta-tools"),
    ("SERP Snippet Preview", "meta-tools"),
    ("Slug Generator", "content-tools"),
    ("Title Case Converter", "content-tools"),
    ("Plagiarism Checker", "content-tools"),
    # Backlink Tools
    ("Backlink Quality Checker", "backlink-tools"),
    ("Domain Authority Estimator", "backlink-tools"),
    ("Anchor Text Distribution", "backlink-tools"),
    ("Broken Link Finder", "backlink-tools"),
    ("Linkable Asset Idea Generator", "backlink-tools"),
    # Local SEO Tools
    ("NAP Consistency Checker", "local-seo-tools"),
    ("Citation Audit Tool", "local-seo-tools"),
    ("Google Business Profile Audit", "local-seo-tools"),
    ("Local Schema Generator", "local-seo-tools"),
    ("Map Pack Position Tracker", "local-seo-tools"),
    ("Geo Modifier Generator", "local-seo-tools"),
    # AI SEO Tools
    ("AI Overview Visibility Checker", "ai-seo-tools"),
    ("ChatGPT Citation Tracker", "ai-seo-tools"),
    ("Perplexity Citation Tracker", "ai-seo-tools"),
    ("AI Content Detector", "ai-seo-tools"),
    ("AI Title Generator", "ai-seo-tools"),
    ("AI FAQ Generator", "ai-seo-tools"),
    ("AI Meta Description Generator", "ai-seo-tools"),
    ("AI Schema Generator", "ai-seo-tools"),
    # Schema Tools (under meta)
    ("FAQ Schema Generator", "meta-tools"),
    ("HowTo Schema Generator", "meta-tools"),
    ("Article Schema Generator", "meta-tools"),
    ("Product Schema Generator", "meta-tools"),
    ("LocalBusiness Schema Generator", "meta-tools"),
    ("Breadcrumb Schema Generator", "meta-tools"),
    ("VideoObject Schema Generator", "meta-tools"),
    ("Review Schema Generator", "meta-tools"),
    ("Event Schema Generator", "meta-tools"),
    # PPC Tools
    ("CPC Calculator", "ppc-tools"),
    ("ROAS Calculator", "ppc-tools"),
    ("CTR Calculator", "ppc-tools"),
    ("Quality Score Estimator", "ppc-tools"),
    ("Ad Copy Generator", "ppc-tools"),
    ("UTM Builder", "ppc-tools"),
    ("Negative Keyword Generator", "ppc-tools"),
    # Indexing Tools
    ("Index Coverage Checker", "indexing-tools"),
    ("Bulk Indexing Checker", "indexing-tools"),
    ("Crawl Stats Estimator", "indexing-tools"),
    ("URL Inspector", "indexing-tools"),
    # Conversion Tools
    ("CRO Heuristic Checklist", "conversion-tools"),
    ("Above-the-Fold Tester", "conversion-tools"),
    ("CTA Strength Analyzer", "conversion-tools"),
    ("Form Field Counter", "conversion-tools"),
    ("Page Speed to Conversion Estimator", "conversion-tools"),
    # Reporting Tools
    ("Monthly SEO Report Generator", "reporting-tools"),
    ("KPI Tracker", "reporting-tools"),
    ("Rank Tracking Snapshot", "reporting-tools"),
    ("Traffic Forecaster", "reporting-tools"),
    ("Pipeline Attribution Calculator", "reporting-tools"),
    # Social Tools
    ("Hashtag Generator", "social-tools"),
    ("LinkedIn Post Optimizer", "social-tools"),
    ("Twitter Bio Optimizer", "social-tools"),
    ("Instagram Caption Generator", "social-tools"),
    ("YouTube Title Optimizer", "social-tools"),
    ("YouTube Tag Generator", "social-tools"),
    ("Pinterest Pin Title Generator", "social-tools"),
    ("TikTok Hook Generator", "social-tools"),
    ("Social Share Image Sizer", "social-tools"),
    # Bonus tools to push to 85
    ("URL Shortener", "content-tools"),
    ("HTML Encoder Decoder", "technical-seo-tools"),
    ("HTACCESS Generator", "technical-seo-tools"),
    ("Schema Validator", "meta-tools"),
    ("Robots.txt Generator", "technical-seo-tools"),
]


def build_tools() -> list[dict]:
    out = []
    for name, cat in TOOL_SEED:
        slug = slugify(name)
        out.append(
            {
                "slug": slug,
                "name": name,
                "primaryKeyword": f"free {name.lower()}",
                "lsiKeywords": [
                    f"online {name.lower()}",
                    f"{name.lower()} tool",
                    f"best {name.lower()}",
                    f"{name.lower()} for SEO",
                    f"{name.lower()} 2026",
                ],
                "shortDescription": (
                    f"Free {name.lower()} - run unlimited checks in your browser, no signup required."
                ),
                "heroImagePrompt": f"product UI mock of {name.lower()} on dark navy background with electric blue accents",
                "parentCategory": cat,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Countries (55+) and cities (top metros, ~252)
# ---------------------------------------------------------------------------

COUNTRY_SEED: list[tuple[str, str, str, str]] = [
    # (code, name, region_slug, currency)
    ("US", "United States", "north-america", "USD"),
    ("CA", "Canada", "north-america", "CAD"),
    ("MX", "Mexico", "north-america", "MXN"),
    ("GB", "United Kingdom", "europe-west", "GBP"),
    ("IE", "Ireland", "europe-west", "EUR"),
    ("FR", "France", "europe-west", "EUR"),
    ("DE", "Germany", "europe-west", "EUR"),
    ("NL", "Netherlands", "europe-west", "EUR"),
    ("BE", "Belgium", "europe-west", "EUR"),
    ("LU", "Luxembourg", "europe-west", "EUR"),
    ("AT", "Austria", "europe-west", "EUR"),
    ("CH", "Switzerland", "europe-west", "CHF"),
    ("ES", "Spain", "europe-west", "EUR"),
    ("PT", "Portugal", "europe-west", "EUR"),
    ("IT", "Italy", "europe-west", "EUR"),
    ("MT", "Malta", "europe-west", "EUR"),
    ("SE", "Sweden", "europe-nordic-east", "SEK"),
    ("NO", "Norway", "europe-nordic-east", "NOK"),
    ("DK", "Denmark", "europe-nordic-east", "DKK"),
    ("FI", "Finland", "europe-nordic-east", "EUR"),
    ("IS", "Iceland", "europe-nordic-east", "ISK"),
    ("PL", "Poland", "europe-nordic-east", "PLN"),
    ("CZ", "Czech Republic", "europe-nordic-east", "CZK"),
    ("SK", "Slovakia", "europe-nordic-east", "EUR"),
    ("HU", "Hungary", "europe-nordic-east", "HUF"),
    ("RO", "Romania", "europe-nordic-east", "RON"),
    ("BG", "Bulgaria", "europe-nordic-east", "BGN"),
    ("GR", "Greece", "europe-nordic-east", "EUR"),
    ("EE", "Estonia", "europe-nordic-east", "EUR"),
    ("LV", "Latvia", "europe-nordic-east", "EUR"),
    ("LT", "Lithuania", "europe-nordic-east", "EUR"),
    ("HR", "Croatia", "europe-nordic-east", "EUR"),
    ("SI", "Slovenia", "europe-nordic-east", "EUR"),
    ("RS", "Serbia", "europe-nordic-east", "RSD"),
    ("UA", "Ukraine", "europe-nordic-east", "UAH"),
    ("AE", "United Arab Emirates", "middle-east", "AED"),
    ("SA", "Saudi Arabia", "middle-east", "SAR"),
    ("QA", "Qatar", "middle-east", "QAR"),
    ("KW", "Kuwait", "middle-east", "KWD"),
    ("BH", "Bahrain", "middle-east", "BHD"),
    ("OM", "Oman", "middle-east", "OMR"),
    ("JO", "Jordan", "middle-east", "JOD"),
    ("IL", "Israel", "middle-east", "ILS"),
    ("TR", "Turkey", "middle-east", "TRY"),
    ("EG", "Egypt", "middle-east", "EGP"),
    ("IN", "India", "south-asia", "INR"),
    ("PK", "Pakistan", "south-asia", "PKR"),
    ("BD", "Bangladesh", "south-asia", "BDT"),
    ("LK", "Sri Lanka", "south-asia", "LKR"),
    ("NP", "Nepal", "south-asia", "NPR"),
    ("CN", "China", "east-asia", "CNY"),
    ("JP", "Japan", "east-asia", "JPY"),
    ("KR", "South Korea", "east-asia", "KRW"),
    ("HK", "Hong Kong", "east-asia", "HKD"),
    ("TW", "Taiwan", "east-asia", "TWD"),
    ("SG", "Singapore", "east-asia", "SGD"),
    ("MY", "Malaysia", "east-asia", "MYR"),
    ("TH", "Thailand", "east-asia", "THB"),
    ("VN", "Vietnam", "east-asia", "VND"),
    ("ID", "Indonesia", "east-asia", "IDR"),
    ("PH", "Philippines", "east-asia", "PHP"),
    ("AU", "Australia", "oceania", "AUD"),
    ("NZ", "New Zealand", "oceania", "NZD"),
    ("BR", "Brazil", "latin-africa", "BRL"),
    ("AR", "Argentina", "latin-africa", "ARS"),
    ("CL", "Chile", "latin-africa", "CLP"),
    ("CO", "Colombia", "latin-africa", "COP"),
    ("PE", "Peru", "latin-africa", "PEN"),
    ("ZA", "South Africa", "latin-africa", "ZAR"),
    ("NG", "Nigeria", "latin-africa", "NGN"),
    ("KE", "Kenya", "latin-africa", "KES"),
    ("MA", "Morocco", "latin-africa", "MAD"),
    ("TN", "Tunisia", "latin-africa", "TND"),
    ("GH", "Ghana", "latin-africa", "GHS"),
]

CITY_SEED: list[tuple[str, str]] = [
    # (city_name, country_code)
    # USA - top metros
    ("New York", "US"), ("Los Angeles", "US"), ("Chicago", "US"), ("Houston", "US"),
    ("Phoenix", "US"), ("Philadelphia", "US"), ("San Antonio", "US"), ("San Diego", "US"),
    ("Dallas", "US"), ("Austin", "US"), ("San Francisco", "US"), ("Seattle", "US"),
    ("Denver", "US"), ("Boston", "US"), ("Miami", "US"), ("Atlanta", "US"),
    ("Las Vegas", "US"), ("Portland", "US"), ("Nashville", "US"), ("Washington DC", "US"),
    # Canada
    ("Toronto", "CA"), ("Vancouver", "CA"), ("Montreal", "CA"), ("Calgary", "CA"),
    ("Edmonton", "CA"), ("Ottawa", "CA"), ("Mississauga", "CA"),
    # Mexico
    ("Mexico City", "MX"), ("Guadalajara", "MX"), ("Monterrey", "MX"),
    # UK
    ("London", "GB"), ("Manchester", "GB"), ("Birmingham", "GB"), ("Edinburgh", "GB"),
    ("Glasgow", "GB"), ("Liverpool", "GB"), ("Bristol", "GB"), ("Leeds", "GB"),
    # Ireland
    ("Dublin", "IE"), ("Cork", "IE"),
    # France
    ("Paris", "FR"), ("Lyon", "FR"), ("Marseille", "FR"), ("Toulouse", "FR"),
    ("Nice", "FR"), ("Bordeaux", "FR"),
    # Germany
    ("Berlin", "DE"), ("Munich", "DE"), ("Hamburg", "DE"), ("Frankfurt", "DE"),
    ("Cologne", "DE"), ("Stuttgart", "DE"), ("Düsseldorf", "DE"),
    # Netherlands
    ("Amsterdam", "NL"), ("Rotterdam", "NL"), ("The Hague", "NL"), ("Utrecht", "NL"),
    ("Eindhoven", "NL"),
    # Belgium
    ("Brussels", "BE"), ("Antwerp", "BE"), ("Ghent", "BE"),
    # Luxembourg
    ("Luxembourg City", "LU"),
    # Austria
    ("Vienna", "AT"), ("Salzburg", "AT"),
    # Switzerland
    ("Zurich", "CH"), ("Geneva", "CH"), ("Basel", "CH"), ("Bern", "CH"),
    # Spain
    ("Madrid", "ES"), ("Barcelona", "ES"), ("Valencia", "ES"), ("Seville", "ES"),
    ("Bilbao", "ES"), ("Malaga", "ES"),
    # Portugal
    ("Lisbon", "PT"), ("Porto", "PT"),
    # Italy
    ("Rome", "IT"), ("Milan", "IT"), ("Naples", "IT"), ("Turin", "IT"),
    ("Florence", "IT"), ("Bologna", "IT"),
    # Malta
    ("Valletta", "MT"),
    # Sweden
    ("Stockholm", "SE"), ("Gothenburg", "SE"), ("Malmö", "SE"),
    # Norway
    ("Oslo", "NO"), ("Bergen", "NO"), ("Trondheim", "NO"),
    # Denmark
    ("Copenhagen", "DK"), ("Aarhus", "DK"),
    # Finland
    ("Helsinki", "FI"), ("Tampere", "FI"),
    # Iceland
    ("Reykjavik", "IS"),
    # Poland
    ("Warsaw", "PL"), ("Krakow", "PL"), ("Wroclaw", "PL"), ("Gdansk", "PL"),
    # Czech
    ("Prague", "CZ"), ("Brno", "CZ"),
    # Slovakia
    ("Bratislava", "SK"),
    # Hungary
    ("Budapest", "HU"),
    # Romania
    ("Bucharest", "RO"), ("Cluj-Napoca", "RO"), ("Timisoara", "RO"),
    # Bulgaria
    ("Sofia", "BG"), ("Plovdiv", "BG"),
    # Greece
    ("Athens", "GR"), ("Thessaloniki", "GR"),
    # Baltics
    ("Tallinn", "EE"), ("Riga", "LV"), ("Vilnius", "LT"),
    # Croatia / Slovenia
    ("Zagreb", "HR"), ("Split", "HR"), ("Ljubljana", "SI"),
    # Serbia
    ("Belgrade", "RS"), ("Novi Sad", "RS"),
    # Ukraine
    ("Kyiv", "UA"), ("Lviv", "UA"),
    # UAE
    ("Dubai", "AE"), ("Abu Dhabi", "AE"), ("Sharjah", "AE"), ("Ajman", "AE"),
    ("Ras Al Khaimah", "AE"), ("Fujairah", "AE"),
    # Saudi Arabia
    ("Riyadh", "SA"), ("Jeddah", "SA"), ("Dammam", "SA"), ("Mecca", "SA"), ("Medina", "SA"),
    # Qatar
    ("Doha", "QA"),
    # Kuwait
    ("Kuwait City", "KW"),
    # Bahrain
    ("Manama", "BH"),
    # Oman
    ("Muscat", "OM"),
    # Jordan
    ("Amman", "JO"),
    # Israel
    ("Tel Aviv", "IL"), ("Jerusalem", "IL"), ("Haifa", "IL"),
    # Turkey
    ("Istanbul", "TR"), ("Ankara", "TR"), ("Izmir", "TR"), ("Antalya", "TR"),
    # Egypt
    ("Cairo", "EG"), ("Alexandria", "EG"),
    # India
    ("Mumbai", "IN"), ("Delhi", "IN"), ("Bangalore", "IN"), ("Hyderabad", "IN"),
    ("Chennai", "IN"), ("Kolkata", "IN"), ("Pune", "IN"), ("Ahmedabad", "IN"),
    ("Jaipur", "IN"), ("Lucknow", "IN"), ("Chandigarh", "IN"), ("Gurgaon", "IN"), ("Noida", "IN"),
    # Pakistan
    ("Karachi", "PK"), ("Lahore", "PK"), ("Islamabad", "PK"), ("Rawalpindi", "PK"), ("Faisalabad", "PK"),
    # Bangladesh
    ("Dhaka", "BD"), ("Chittagong", "BD"),
    # Sri Lanka
    ("Colombo", "LK"),
    # Nepal
    ("Kathmandu", "NP"),
    # China
    ("Beijing", "CN"), ("Shanghai", "CN"), ("Shenzhen", "CN"), ("Guangzhou", "CN"),
    ("Chengdu", "CN"), ("Hangzhou", "CN"),
    # Japan
    ("Tokyo", "JP"), ("Osaka", "JP"), ("Kyoto", "JP"), ("Yokohama", "JP"),
    ("Nagoya", "JP"), ("Fukuoka", "JP"),
    # Korea
    ("Seoul", "KR"), ("Busan", "KR"), ("Incheon", "KR"),
    # HK / TW
    ("Hong Kong", "HK"), ("Taipei", "TW"), ("Kaohsiung", "TW"),
    # Singapore
    ("Singapore", "SG"),
    # Malaysia
    ("Kuala Lumpur", "MY"), ("Penang", "MY"), ("Johor Bahru", "MY"),
    # Thailand
    ("Bangkok", "TH"), ("Chiang Mai", "TH"), ("Phuket", "TH"),
    # Vietnam
    ("Ho Chi Minh City", "VN"), ("Hanoi", "VN"), ("Da Nang", "VN"),
    # Indonesia
    ("Jakarta", "ID"), ("Surabaya", "ID"), ("Bali", "ID"),
    # Philippines
    ("Manila", "PH"), ("Cebu", "PH"),
    # Australia
    ("Sydney", "AU"), ("Melbourne", "AU"), ("Brisbane", "AU"), ("Perth", "AU"),
    ("Adelaide", "AU"), ("Gold Coast", "AU"),
    # New Zealand
    ("Auckland", "NZ"), ("Wellington", "NZ"), ("Christchurch", "NZ"),
    # Brazil
    ("Sao Paulo", "BR"), ("Rio de Janeiro", "BR"), ("Brasilia", "BR"),
    ("Salvador", "BR"), ("Belo Horizonte", "BR"),
    # Argentina
    ("Buenos Aires", "AR"), ("Cordoba", "AR"),
    # Chile
    ("Santiago", "CL"),
    # Colombia
    ("Bogota", "CO"), ("Medellin", "CO"),
    # Peru
    ("Lima", "PE"),
    # South Africa
    ("Johannesburg", "ZA"), ("Cape Town", "ZA"), ("Durban", "ZA"), ("Pretoria", "ZA"),
    # Nigeria
    ("Lagos", "NG"), ("Abuja", "NG"),
    # Kenya
    ("Nairobi", "KE"), ("Mombasa", "KE"),
    # Morocco
    ("Casablanca", "MA"), ("Marrakech", "MA"), ("Rabat", "MA"),
    # Tunisia
    ("Tunis", "TN"),
    # Ghana
    ("Accra", "GH"),
]


def build_countries() -> list[dict]:
    out = []
    for code, name, region, currency in COUNTRY_SEED:
        out.append(
            {
                "code": code,
                "slug": slugify(name),
                "name": name,
                "region": region,
                "currency": currency,
                "primaryKeyword": f"SEO services in {name}",
                "lsiKeywords": [
                    f"digital marketing {name}",
                    f"PPC management {name}",
                    f"local SEO {name}",
                    f"SEO agency {name}",
                    f"SEO expert {name}",
                ],
                "shortDescription": (
                    f"SEO and digital marketing tailored for businesses in {name}, with bilingual content "
                    "and locally optimized link building, citations, and ad campaigns."
                ),
                "heroImagePrompt": f"skyline of major city in {name} with subtle dark navy and electric blue overlay",
            }
        )
    return out


def build_cities() -> list[dict]:
    out = []
    for city_name, country_code in CITY_SEED:
        out.append(
            {
                "slug": "seo-services-" + slugify(city_name),
                "name": city_name,
                "countryCode": country_code,
                "primaryKeyword": f"SEO services in {city_name}",
                "lsiKeywords": [
                    f"{city_name} SEO agency",
                    f"local SEO {city_name}",
                    f"digital marketing {city_name}",
                    f"PPC management {city_name}",
                    f"{city_name} SEO expert",
                ],
                "shortDescription": (
                    f"Local SEO, PPC, and content marketing for {city_name} businesses that want to dominate "
                    "Google Maps, the local pack, and generative search results."
                ),
                "heroImagePrompt": f"skyline of {city_name} at dusk, dark navy filter with electric blue accents",
            }
        )
    return out


# ---------------------------------------------------------------------------
# Blog topics (30) and resources (17)
# ---------------------------------------------------------------------------

BLOG_SEED: list[str] = [
    "GEO vs SEO: How to Get Cited by ChatGPT and Perplexity in 2026",
    "AEO Guide: Engineering Content for Featured Snippets and AI Answers",
    "AI Overviews: A Practical SEO Playbook for SGE in 2026",
    "Core Web Vitals 2026: INP, LCP, and CLS Like an Engineer",
    "Schema Markup That Actually Earns Rich Results",
    "International SEO Hreflang Setup Without Tears",
    "Local SEO Map Pack Domination: 2026 Field Guide",
    "Programmatic SEO at Scale Without Spam",
    "Topic Cluster Architecture for AI Search Era",
    "Link Building Without Link Building: Earn-Mode Outreach",
    "Technical SEO Audit Template Used on 50+ Brand Engagements",
    "Keyword Research for AI Search and Zero-Click Reality",
    "E-commerce SEO: From Product Pages to Performance Max",
    "SaaS SEO: Win Bottom-of-Funnel Buyer Queries",
    "Healthcare SEO Compliance and HIPAA-Friendly Content Ops",
    "Legal SEO Without Bar-Compliance Headaches",
    "Real Estate SEO: Hyper-Local Pages That Capture Buyer Intent",
    "Shopify SEO Checklist 2026",
    "WooCommerce SEO Without Plugin Bloat",
    "Generative SEO Content Briefs that Score Citations",
    "How to Run an AI Visibility Audit (ChatGPT, Perplexity, Claude, Gemini)",
    "PPC and SEO Synergy: Killing the Silos",
    "Google Business Profile Optimization: Beyond the Basics",
    "Backlink Quality Over Quantity: The Modern Definition",
    "How to Pitch SEO Internally to Skeptical Executives",
    "AI Content Detection and How to Build Trust Anyway",
    "Speakable Schema and Voice Search SEO 2026",
    "Hreflang for Multi-Region SaaS",
    "Site Migration SEO: A Pre-Flight Checklist",
    "Measuring SEO ROI: Pipeline-Attributed Metrics That Survive Boardrooms",
]


def build_blog_topics() -> list[dict]:
    out = []
    for title in BLOG_SEED:
        slug = slugify(title)
        out.append(
            {
                "slug": slug,
                "title": title,
                "primaryKeyword": title.split(":")[0].strip().lower(),
                "lsiKeywords": [
                    "SEO 2026",
                    "AI search",
                    "GEO optimization",
                    "AEO optimization",
                    "search visibility",
                ],
                "shortDescription": (
                    "Expert-grade analysis with concrete frameworks, examples, and templates you can apply this quarter."
                ),
                "heroImagePrompt": "abstract editorial graphic on dark navy with electric blue and neon green accents",
                "category": "Insights",
                "datePublished": "2026-01-15",
            }
        )
    return out


RESOURCE_SEED: list[str] = [
    "Free SEO Checklist 2026",
    "Technical SEO Audit Template",
    "Keyword Research Workbook",
    "Content Brief Template",
    "Local SEO Map Pack Playbook",
    "Schema Markup Cheatsheet",
    "Backlink Outreach Email Templates",
    "AI Visibility Audit Workbook",
    "Core Web Vitals Engineer Checklist",
    "Hreflang Implementation Worksheet",
    "PPC Account Audit Template",
    "Monthly SEO Report Template",
    "GEO Content Brief Template",
    "AEO FAQ Block Generator",
    "Google Business Profile Audit Sheet",
    "E-commerce SEO Checklist",
    "Site Migration Pre-Flight Checklist",
]


def build_resources() -> list[dict]:
    out = []
    for title in RESOURCE_SEED:
        slug = slugify(title)
        out.append(
            {
                "slug": slug,
                "name": title,
                "primaryKeyword": title.lower(),
                "lsiKeywords": [
                    "free SEO resource",
                    "SEO download",
                    "SEO template",
                    "SEO checklist",
                    "SEO playbook",
                ],
                "shortDescription": (
                    f"Download {title} - a battle-tested resource we use on real client engagements."
                ),
                "heroImagePrompt": "PDF cover mock with dark navy gradient and electric blue title",
            }
        )
    return out


def main() -> None:
    data = json.loads(DATA.read_text())
    data["industries"] = build_industries()
    data["tools"] = build_tools()
    data["countries"] = build_countries()
    data["cities"] = build_cities()
    data["blogTopics"] = build_blog_topics()
    data["resources"] = build_resources()
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print("services:", len(data["services"]))
    print("ppcServices:", len(data["ppcServices"]))
    print("industries:", len(data["industries"]))
    print("tools:", len(data["tools"]))
    print("countries:", len(data["countries"]))
    print("cities:", len(data["cities"]))
    print("blogTopics:", len(data["blogTopics"]))
    print("resources:", len(data["resources"]))
    print("languages:", len(data["languages"]))


if __name__ == "__main__":
    main()
