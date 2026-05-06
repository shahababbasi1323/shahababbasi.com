#!/usr/bin/env node
/**
 * Static Site Generator for shahababbasi.com
 * Generates all HTML pages from templates and data files.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'src-static');
const DIST = path.join(ROOT, 'dist');
const TEMPLATES = path.join(SRC, 'templates');
const DATA = path.join(SRC, 'data');
const SITE_URL = 'https://shahababbasi.com';

function loadJSON(f) { return JSON.parse(fs.readFileSync(path.join(DATA, f), 'utf8')); }
function loadTemplate(f) { return fs.readFileSync(path.join(TEMPLATES, f), 'utf8'); }

function render(template, data) {
  let r = template;
  for (const [k, v] of Object.entries(data)) {
    r = r.replace(new RegExp(`\\{\\{${k}\\}\\}`, 'g'), v ?? '');
  }
  r = r.replace(/\{\{[a-zA-Z_]+\}\}/g, '');
  return r;
}

function wrapInLayout(content, pd) {
  const layout = loadTemplate('layout.html');
  const header = loadTemplate('header.html');
  const footer = loadTemplate('footer.html');
  const schemas = (pd.schemas || []).map(s => `<script type="application/ld+json">${JSON.stringify(s)}</script>`).join('\n');
  return render(layout, {
    title: pd.title,
    description: pd.description,
    canonical: pd.canonical || `${SITE_URL}${pd.path || '/'}`,
    og_title: pd.og_title || pd.title,
    og_description: pd.og_description || pd.description,
    og_url: pd.canonical || `${SITE_URL}${pd.path || '/'}`,
    og_type: pd.og_type || 'website',
    og_image: pd.og_image || `${SITE_URL}/assets/images/og-default.png`,
    schema_markup: schemas,
    extra_head: pd.extra_head || '',
    header,
    content,
    footer,
    extra_scripts: pd.extra_scripts || '',
  });
}

function writePage(fp, html) {
  const full = path.join(DIST, fp);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, html, 'utf8');
}

function generateSitemap(pages) {
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
  for (const p of pages) {
    xml += `  <url>\n    <loc>${SITE_URL}${p.path}</loc>\n    <lastmod>${p.lastmod || new Date().toISOString().split('T')[0]}</lastmod>\n    <changefreq>${p.changefreq || 'monthly'}</changefreq>\n    <priority>${p.priority || '0.5'}</priority>\n  </url>\n`;
  }
  xml += '</urlset>';
  return xml;
}

// ─── BUILD ──────────────────────────────────────────────────────
console.log('Building static site...\n');

if (fs.existsSync(DIST)) fs.rmSync(DIST, { recursive: true });
fs.mkdirSync(DIST, { recursive: true });

// Copy assets
console.log('Copying assets...');
const assetsSrc = path.join(SRC, 'assets');
function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const e of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, e.name), d = path.join(dest, e.name);
    e.isDirectory() ? copyDir(s, d) : fs.copyFileSync(s, d);
  }
}
copyDir(assetsSrc, path.join(DIST, 'assets'));

// Copy public files (indexnow key, etc)
const publicDir = path.join(ROOT, 'public');
if (fs.existsSync(publicDir)) {
  for (const e of fs.readdirSync(publicDir, { withFileTypes: true })) {
    if (e.name === 'index.html') continue;
    const s = path.join(publicDir, e.name), d = path.join(DIST, e.name);
    e.isDirectory() ? copyDir(s, d) : fs.copyFileSync(s, d);
  }
}

const sitemapPages = [];
let pageCount = 0;

// Load all data
const corePages = loadJSON('core-pages.json');
const services = loadJSON('services.json');
const industries = loadJSON('industries.json');
const locations = loadJSON('locations.json');
const tools = loadJSON('tools.json');
const blogPosts = loadJSON('blog-posts.json');
const ppcServices = loadJSON('ppc-services.json');
const countryHubs = loadJSON('country-hubs.json');
const resources = loadJSON('resources.json');

// ─── HELPER: Build blog cards ───────────────────────────────────
function blogCardsHTML() {
  return blogPosts.map(p => `<div class="blog-card"><div class="blog-card-body"><div class="blog-meta"><span>${p.category}</span><span>${p.date}</span><span>${p.read_time}</span></div><h3><a href="/blog/${p.slug}">${p.title}</a></h3><p class="blog-excerpt">${p.excerpt}</p><a href="/blog/${p.slug}" class="card-link">Read More &rarr;</a></div></div>`).join('\n');
}

// ─── HELPER: Build tool cards ───────────────────────────────────
function toolCardsHTML() {
  const cats = {};
  tools.forEach(t => { if (!cats[t.category]) cats[t.category] = []; cats[t.category].push(t); });
  let h = '';
  for (const [c, items] of Object.entries(cats)) {
    h += `<div style="grid-column:1/-1;"><h3 style="margin:1.5rem 0 .75rem;">${c} <span class="text-muted" style="font-size:.85rem;font-weight:400;">(${items.length} tools)</span></h3></div>`;
    items.forEach(t => { h += `<a href="/tools/${t.slug}" class="card tool-card"><span class="card-category">${t.category}</span><h3>${t.name}</h3><p>${t.description}</p><span class="card-link">Use Tool &rarr;</span></a>`; });
  }
  return h;
}

// ─── HELPER: Build service cards ────────────────────────────────
function serviceCardsHTML() {
  return services.map(s => `<a href="/services/${s.slug}" class="card"><h3>${s.name}</h3><p>${s.hero_description}</p><span class="card-link">Learn more &rarr;</span></a>`).join('\n');
}

// ─── HELPER: Build industry cards ───────────────────────────────
function industryCardsHTML() {
  const cats = {};
  industries.forEach(i => { if (!cats[i.category]) cats[i.category] = []; cats[i.category].push(i); });
  let h = '';
  for (const [c, items] of Object.entries(cats)) {
    h += `<div style="grid-column:1/-1;"><h3 style="margin:1.5rem 0 .75rem;">${c}</h3></div>`;
    items.forEach(i => { h += `<a href="/industries/${i.slug}" class="card"><h3>${i.short_title}</h3><p>${i.hero_description}</p><span class="card-link">Learn more &rarr;</span></a>`; });
  }
  return h;
}

// ─── HELPER: Location groups ────────────────────────────────────
function locationGroupsHTML() {
  const byCountry = {};
  locations.forEach(l => { if (!byCountry[l.country]) byCountry[l.country] = []; byCountry[l.country].push(l); });
  let h = '';
  for (const [co, cities] of Object.entries(byCountry)) {
    h += `<div class="location-group"><h3>${co} (${cities.length})</h3><div class="location-list">`;
    cities.forEach(c => { h += `<a href="/locations/${c.slug}">${c.city}</a>`; });
    h += '</div></div>';
  }
  return h;
}

// ─── HELPER: Country hub cards ──────────────────────────────────
function countryHubCardsHTML() {
  return countryHubs.map(c => `<a href="/locations/${c.slug}" class="card"><h3>${c.name}</h3><p>${c.hero_description}</p><span class="card-link">View cities &rarr;</span></a>`).join('\n');
}

// ─── HELPER: PPC cards ──────────────────────────────────────────
function ppcCardsHTML() {
  return ppcServices.map(p => `<a href="/ppc/${p.slug}" class="card"><h3>${p.name}</h3><p>${p.hero_description}</p><span class="card-link">Learn more &rarr;</span></a>`).join('\n');
}

// ─── HELPER: Resource cards ─────────────────────────────────────
function resourceCardsHTML() {
  return resources.map(r => `<div class="card"><span class="card-category">${r.category}</span><h3>${r.title}</h3><p>${r.description}</p></div>`).join('\n');
}

// ─── CORE PAGES ─────────────────────────────────────────────────
console.log('Building core pages...');
for (const page of corePages) {
  let tpl = loadTemplate(page.template);
  // Inject dynamic content
  tpl = tpl.replace('{{blog_cards}}', blogCardsHTML());
  tpl = tpl.replace('{{tool_cards}}', toolCardsHTML());
  tpl = tpl.replace('{{service_cards}}', serviceCardsHTML());
  tpl = tpl.replace('{{industry_cards}}', industryCardsHTML());
  tpl = tpl.replace('{{location_groups}}', locationGroupsHTML());
  tpl = tpl.replace('{{country_hub_cards}}', countryHubCardsHTML());
  tpl = tpl.replace('{{ppc_cards}}', ppcCardsHTML());
  tpl = tpl.replace('{{resource_cards}}', resourceCardsHTML());
  const html = wrapInLayout(tpl, page);
  writePage(page.output, html);
  if (!page.noindex) sitemapPages.push({ path: page.path, priority: page.priority || '0.8', changefreq: page.changefreq || 'weekly' });
  pageCount++;
}

// ─── SERVICE PAGES ──────────────────────────────────────────────
console.log('Building service pages...');
const svcTpl = loadTemplate('service-detail.html');
for (const svc of services) {
  const content = render(svcTpl, {
    ...svc,
    benefits_html: (svc.benefits || []).map(b => `<div class="service-benefit">${b}</div>`).join(''),
    process_html: (svc.process_steps || []).map(s => `<div class="process-step"><div><h3>${s.title}</h3><p>${s.desc}</p></div></div>`).join(''),
    tools_html: (svc.tools_used || []).map(t => `<span class="tool-tag">${t}</span>`).join(''),
    deliverables_html: (svc.deliverables || []).map(d => `<div class="service-benefit">${d}</div>`).join(''),
    faq_html: (svc.faqs || []).map(f => `<div class="faq-item"><button class="faq-question">${f.q}</button><div class="faq-answer"><div class="faq-answer-inner">${f.a}</div></div></div>`).join(''),
    related_services_html: (svc.related_services || []).map(rs => { const found = services.find(s => s.slug === rs); return found ? `<a href="/services/${rs}" class="card"><h3>${found.name}</h3></a>` : ''; }).join(''),
  });
  const html = wrapInLayout(content, {
    title: svc.meta_title,
    description: svc.meta_description,
    path: `/services/${svc.slug}`,
    schemas: [
      { '@context': 'https://schema.org', '@type': 'Service', name: svc.name, description: svc.meta_description, provider: { '@type': 'Person', name: 'Shahab Abbasi', url: SITE_URL }, areaServed: 'Worldwide' },
      { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL }, { '@type': 'ListItem', position: 2, name: 'Services', item: `${SITE_URL}/services` }, { '@type': 'ListItem', position: 3, name: svc.name, item: `${SITE_URL}/services/${svc.slug}` }] },
      ...(svc.faqs && svc.faqs.length ? [{ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: svc.faqs.map(f => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })) }] : []),
    ],
  });
  writePage(`services/${svc.slug}/index.html`, html);
  sitemapPages.push({ path: `/services/${svc.slug}`, priority: '0.7', changefreq: 'monthly' });
  pageCount++;
}

// ─── INDUSTRY PAGES ─────────────────────────────────────────────
console.log('Building industry pages...');
const indTpl = loadTemplate('industry-detail.html');
for (const ind of industries) {
  const content = render(indTpl, {
    ...ind,
    challenges_html: (ind.challenges || []).map(c => `<div class="card"><h3>${c.title}</h3><p>${c.desc}</p></div>`).join(''),
    approach_html: (ind.approach || []).map(a => `<div class="process-step"><div><h3>${a.title}</h3><p>${a.desc}</p></div></div>`).join(''),
    keywords_html: (ind.keywords || []).map(k => `<span class="tool-tag">${k}</span>`).join(''),
    case_study_html: (ind.case_study || []).map(c => `<div class="stat-item"><div class="stat-number">${c.metric}</div><div class="stat-label">${c.label}</div></div>`).join(''),
    faq_html: (ind.faqs || []).map(f => `<div class="faq-item"><button class="faq-question">${f.q}</button><div class="faq-answer"><div class="faq-answer-inner">${f.a}</div></div></div>`).join(''),
    related_services_html: (ind.related_services || []).map(rs => { const found = services.find(s => s.slug === rs); return found ? `<a href="/services/${rs}" class="card"><h3>${found.name}</h3></a>` : ''; }).join(''),
    related_locations_html: (ind.related_locations || []).map(rl => { const found = locations.find(l => l.slug.includes(rl)); return found ? `<a href="/locations/${found.slug}" class="card"><h3>${found.city}</h3></a>` : ''; }).join(''),
  });
  const html = wrapInLayout(content, {
    title: ind.meta_title,
    description: ind.meta_description,
    path: `/industries/${ind.slug}`,
    schemas: [
      { '@context': 'https://schema.org', '@type': 'Service', name: `SEO for ${ind.short_title}`, description: ind.meta_description, provider: { '@type': 'Person', name: 'Shahab Abbasi', url: SITE_URL } },
      { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL }, { '@type': 'ListItem', position: 2, name: 'Industries', item: `${SITE_URL}/industries` }, { '@type': 'ListItem', position: 3, name: ind.short_title, item: `${SITE_URL}/industries/${ind.slug}` }] },
      ...(ind.faqs && ind.faqs.length ? [{ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: ind.faqs.map(f => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })) }] : []),
    ],
  });
  writePage(`industries/${ind.slug}/index.html`, html);
  sitemapPages.push({ path: `/industries/${ind.slug}`, priority: '0.6', changefreq: 'monthly' });
  pageCount++;
}

// ─── BLOG POSTS ─────────────────────────────────────────────────
console.log('Building blog posts...');
const blogTpl = loadTemplate('blog-post.html');
for (const post of blogPosts) {
  const sections_html = (post.sections || []).map(s => `<section id="${s.id}"><h2>${s.title}</h2><div>${s.content.replace(/\n/g, '<br>')}</div></section>`).join('\n');
  const toc_html = (post.sections || []).map(s => `<li><a href="#${s.id}">${s.title}</a></li>`).join('');
  const faq_html = (post.faqs || []).map(f => `<div class="faq-item"><button class="faq-question">${f.q}</button><div class="faq-answer"><div class="faq-answer-inner">${f.a}</div></div></div>`).join('');
  const content = render(blogTpl, { ...post, sections_html, toc_html, faq_html });
  const html = wrapInLayout(content, {
    title: post.meta_title || `${post.title} | Shahab Abbasi`,
    description: post.meta_description || post.excerpt,
    path: `/blog/${post.slug}`,
    og_type: 'article',
    schemas: [
      { '@context': 'https://schema.org', '@type': 'BlogPosting', headline: post.title, description: post.excerpt, author: { '@type': 'Person', name: 'Shahab Abbasi' }, datePublished: post.date, publisher: { '@type': 'Person', name: 'Shahab Abbasi' } },
      { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL }, { '@type': 'ListItem', position: 2, name: 'Blog', item: `${SITE_URL}/blog` }, { '@type': 'ListItem', position: 3, name: post.title, item: `${SITE_URL}/blog/${post.slug}` }] },
      ...(post.faqs && post.faqs.length ? [{ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: post.faqs.map(f => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })) }] : []),
    ],
  });
  writePage(`blog/${post.slug}/index.html`, html);
  sitemapPages.push({ path: `/blog/${post.slug}`, priority: '0.6', changefreq: 'monthly' });
  pageCount++;
}

// ─── TOOL PAGES ─────────────────────────────────────────────────
console.log('Building tool pages...');
const toolTpl = loadTemplate('tool-detail.html');
for (const tool of tools) {
  const content = render(toolTpl, tool);
  const specificJs = path.join(SRC, 'assets', 'js', 'tools', `${tool.slug}.js`);
  const jsFile = fs.existsSync(specificJs) ? `/assets/js/tools/${tool.slug}.js` : '/assets/js/tools/generic-tool.js';
  const html = wrapInLayout(content, {
    title: `${tool.name} - Free SEO Tool | Shahab Abbasi`,
    description: tool.meta_description,
    path: `/tools/${tool.slug}`,
    extra_scripts: tool.has_js !== false ? `<script src="${jsFile}" defer></script>` : '',
    schemas: [
      { '@context': 'https://schema.org', '@type': 'WebApplication', name: tool.name, description: tool.description, applicationCategory: 'SEO Tool', operatingSystem: 'Web', offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' } },
      { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL }, { '@type': 'ListItem', position: 2, name: 'Free SEO Tools', item: `${SITE_URL}/tools` }, { '@type': 'ListItem', position: 3, name: tool.name, item: `${SITE_URL}/tools/${tool.slug}` }] },
    ],
  });
  writePage(`tools/${tool.slug}/index.html`, html);
  sitemapPages.push({ path: `/tools/${tool.slug}`, priority: '0.5', changefreq: 'monthly' });
  pageCount++;
}

// ─── LOCATION PAGES ─────────────────────────────────────────────
console.log('Building location pages...');
const locTpl = loadTemplate('location-detail.html');
for (const loc of locations) {
  const content = render(locTpl, {
    ...loc,
    challenges_html: (loc.challenges || []).map(c => `<div class="card"><h3>${c.title}</h3><p>${c.desc}</p></div>`).join(''),
    process_html: (loc.process_steps || []).map(s => `<div class="process-step"><div><h3>${s.title}</h3><p>${s.desc}</p></div></div>`).join(''),
    results_html: (loc.results || []).map(r => `<div class="stat-item"><div class="stat-number">${r.stat}</div><div class="stat-label">${r.label}</div></div>`).join(''),
    faq_html: (loc.faqs || []).map(f => `<div class="faq-item"><button class="faq-question">${f.q}</button><div class="faq-answer"><div class="faq-answer-inner">${f.a}</div></div></div>`).join(''),
    nearby_html: (loc.nearby || []).map(n => { const found = locations.find(l => l.slug === n); return found ? `<a href="/locations/${n}" class="tag">${found.city}</a>` : ''; }).join(''),
    services_html: services.slice(0, 8).map(s => `<a href="/services/${s.slug}" class="card"><h3>${s.name}</h3><p>${s.hero_description.substring(0, 100)}...</p></a>`).join(''),
  });
  const html = wrapInLayout(content, {
    title: `SEO & Digital Marketing in ${loc.city}, ${loc.country} | Shahab Abbasi`,
    description: loc.meta_description,
    path: `/locations/${loc.slug}`,
    schemas: [
      { '@context': 'https://schema.org', '@type': 'LocalBusiness', name: 'Shahab Abbasi SEO Services', description: `SEO & digital marketing services in ${loc.city}, ${loc.country}`, areaServed: { '@type': 'City', name: loc.city } },
      { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL }, { '@type': 'ListItem', position: 2, name: 'Locations', item: `${SITE_URL}/locations` }, { '@type': 'ListItem', position: 3, name: `${loc.city}, ${loc.country}`, item: `${SITE_URL}/locations/${loc.slug}` }] },
      ...(loc.faqs && loc.faqs.length ? [{ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: loc.faqs.map(f => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })) }] : []),
    ],
  });
  writePage(`locations/${loc.slug}/index.html`, html);
  sitemapPages.push({ path: `/locations/${loc.slug}`, priority: '0.4', changefreq: 'monthly' });
  pageCount++;
}

// ─── COUNTRY HUB PAGES ─────────────────────────────────────────
console.log('Building country hub pages...');
const countryTpl = loadTemplate('country-hub.html');
for (const hub of countryHubs) {
  const hubCities = locations.filter(l => l.country_code === hub.country_code);
  const cities_html = hubCities.map(c => `<a href="/locations/${c.slug}" class="card"><h3>${c.city}</h3><p>SEO & Digital Marketing Services</p></a>`).join('');
  const why_html = Array.isArray(hub.why_content) ? hub.why_content.map(p => `<p>${p}</p>`).join('') : `<p>${hub.why_content || ''}</p>`;
  const content = render(countryTpl, { ...hub, cities_html, city_count: hubCities.length.toString(), why_content: why_html });
  const html = wrapInLayout(content, {
    title: hub.meta_title,
    description: hub.meta_description,
    path: `/locations/${hub.slug}`,
    schemas: [
      { '@context': 'https://schema.org', '@type': 'Organization', name: 'Shahab Abbasi SEO Services', areaServed: { '@type': 'Country', name: hub.name } },
      { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL }, { '@type': 'ListItem', position: 2, name: 'Locations', item: `${SITE_URL}/locations` }, { '@type': 'ListItem', position: 3, name: hub.name, item: `${SITE_URL}/locations/${hub.slug}` }] },
    ],
  });
  writePage(`locations/${hub.slug}/index.html`, html);
  sitemapPages.push({ path: `/locations/${hub.slug}`, priority: '0.5', changefreq: 'monthly' });
  pageCount++;
}

// ─── PPC SERVICE PAGES ──────────────────────────────────────────
console.log('Building PPC service pages...');
const ppcTpl = loadTemplate('ppc-detail.html');
for (const ppc of ppcServices) {
  const content = render(ppcTpl, {
    ...ppc,
    features_html: (ppc.features || []).map(f => `<div class="service-benefit">${f}</div>`).join(''),
    process_html: (ppc.process_steps || []).map(s => `<div class="process-step"><div><h3>${s.title}</h3><p>${s.desc}</p></div></div>`).join(''),
    faq_html: (ppc.faqs || []).map(f => `<div class="faq-item"><button class="faq-question">${f.q}</button><div class="faq-answer"><div class="faq-answer-inner">${f.a}</div></div></div>`).join(''),
  });
  const html = wrapInLayout(content, {
    title: ppc.meta_title,
    description: ppc.meta_description,
    path: `/ppc/${ppc.slug}`,
    schemas: [
      { '@context': 'https://schema.org', '@type': 'Service', name: ppc.name, description: ppc.meta_description, provider: { '@type': 'Person', name: 'Shahab Abbasi', url: SITE_URL } },
      { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL }, { '@type': 'ListItem', position: 2, name: 'PPC Services', item: `${SITE_URL}/ppc` }, { '@type': 'ListItem', position: 3, name: ppc.name, item: `${SITE_URL}/ppc/${ppc.slug}` }] },
      ...(ppc.faqs && ppc.faqs.length ? [{ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: ppc.faqs.map(f => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })) }] : []),
    ],
  });
  writePage(`ppc/${ppc.slug}/index.html`, html);
  sitemapPages.push({ path: `/ppc/${ppc.slug}`, priority: '0.6', changefreq: 'monthly' });
  pageCount++;
}

// ─── SITEMAP & ROBOTS ───────────────────────────────────────────
console.log('\nGenerating sitemap.xml and robots.txt...');
fs.writeFileSync(path.join(DIST, 'sitemap.xml'), generateSitemap(sitemapPages));
fs.writeFileSync(path.join(DIST, 'robots.txt'), `User-agent: *\nAllow: /\n\nSitemap: ${SITE_URL}/sitemap.xml\n`);

// ─── CLOUDFLARE PAGES CONFIG ────────────────────────────────────
console.log('Generating Cloudflare Pages config...');
fs.writeFileSync(path.join(DIST, '_headers'), `/*\n  X-Frame-Options: DENY\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n\n/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n`);
fs.writeFileSync(path.join(DIST, '_redirects'), `# Clean URL redirects\n/index.html  /  301\n`);

console.log(`\nBuild complete! Generated ${pageCount} pages.`);
console.log(`Sitemap contains ${sitemapPages.length} URLs.`);
