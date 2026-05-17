"""
Tool widget library: maps slug -> HTML+JS widget for /tools/<slug>.html pages.

Every widget is fully client-side, no backend, no tracking. Patterns:
  - Direct text/keyword/url analysis -> immediate calc in browser
  - "Open SERP" tools -> generate Google/AI search URLs and link out
  - Schema/code generators -> form -> formatted output to copy
  - Calculators -> live recalc on input change

Widgets are dispatched by exact slug first, then by substring patterns.
The dispatcher is `widget_for(slug, name)` and is called from generate.py.
"""

from __future__ import annotations


# =============================================================================
# Existing widgets (kept as-is from generate.py, now centralized here)
# =============================================================================

def _word_counter():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste your content</label>
  <textarea id="wc-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 outline-none focus:ring-2 focus:ring-primary"></textarea>
  <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
    <div class="glass p-3"><p class="text-xs text-foreground/60">Words</p><p id="wc-words" class="font-display text-2xl">0</p></div>
    <div class="glass p-3"><p class="text-xs text-foreground/60">Characters</p><p id="wc-chars" class="font-display text-2xl">0</p></div>
    <div class="glass p-3"><p class="text-xs text-foreground/60">Sentences</p><p id="wc-sent" class="font-display text-2xl">0</p></div>
    <div class="glass p-3"><p class="text-xs text-foreground/60">Reading time</p><p id="wc-time" class="font-display text-2xl">0 min</p></div>
  </div>
</div>
<script>
  (function(){
    var t = document.getElementById('wc-input'); if(!t) return;
    function update(){
      var v = t.value;
      var words = (v.trim().match(/\\S+/g) || []).length;
      document.getElementById('wc-words').textContent = words;
      document.getElementById('wc-chars').textContent = v.length;
      document.getElementById('wc-sent').textContent = (v.match(/[^.!?]+[.!?]+/g) || []).length;
      document.getElementById('wc-time').textContent = Math.max(1, Math.round(words / 200)) + ' min';
    }
    t.addEventListener('input', update); update();
  })();
</script>
"""


def _character_counter():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste or type your text</label>
  <textarea id="cc-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 outline-none focus:ring-2 focus:ring-primary"></textarea>
  <div class="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
    <div class="glass p-3"><p class="text-xs text-foreground/60">Characters</p><p id="cc-chars" class="font-display text-2xl">0</p></div>
    <div class="glass p-3"><p class="text-xs text-foreground/60">No spaces</p><p id="cc-nospace" class="font-display text-2xl">0</p></div>
    <div class="glass p-3"><p class="text-xs text-foreground/60">Words</p><p id="cc-words" class="font-display text-2xl">0</p></div>
    <div class="glass p-3"><p class="text-xs text-foreground/60">Lines</p><p id="cc-lines" class="font-display text-2xl">0</p></div>
    <div class="glass p-3"><p class="text-xs text-foreground/60">Paragraphs</p><p id="cc-paras" class="font-display text-2xl">0</p></div>
  </div>
  <p class="mt-3 text-xs text-foreground/60">Common limits: tweet 280 / SMS 160 / meta description 155 / title tag 60.</p>
</div>
<script>
  (function(){
    var t=document.getElementById('cc-input');
    function r(){
      var v=t.value;
      document.getElementById('cc-chars').textContent=v.length;
      document.getElementById('cc-nospace').textContent=v.replace(/\\s/g,'').length;
      document.getElementById('cc-words').textContent=(v.trim().match(/\\S+/g)||[]).length;
      document.getElementById('cc-lines').textContent=v?v.split(/\\r?\\n/).length:0;
      document.getElementById('cc-paras').textContent=v?v.split(/\\n\\s*\\n/).filter(function(p){return p.trim();}).length:0;
    }
    t.addEventListener('input',r); r();
  })();
</script>
"""


def _meta_tag_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Title <input id="mt-title" placeholder="Page title (50-60 chars)" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Description <textarea id="mt-desc" rows="3" placeholder="Meta description (140-160 chars)" class="rounded-lg bg-card/60 border border-border px-3 py-2"></textarea></label>
    <label>Canonical URL <input id="mt-can" placeholder="https://example.com/page" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>OG image URL <input id="mt-og" placeholder="https://example.com/og.png" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Robots <input id="mt-rb" value="index,follow,max-image-preview:large" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
  </form>
  <div>
    <p class="font-display font-semibold mb-2 text-sm">Generated &lt;head&gt; tags</p>
    <pre id="mt-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg"></pre>
    <button id="mt-copy" class="mt-3 inline-flex rounded-xl border border-border/60 px-4 py-2 text-sm hover:bg-white/5">Copy</button>
  </div>
</div>
<script>
  (function(){
    var ids=['mt-title','mt-desc','mt-can','mt-og','mt-rb'].map(function(i){return document.getElementById(i);});
    var out=document.getElementById('mt-out');
    function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
    function r(){
      var t=ids[0].value, d=ids[1].value, c=ids[2].value, og=ids[3].value, rb=ids[4].value;
      var s='';
      if(t) s+='<title>'+esc(t)+'</title>\\n';
      if(d) s+='<meta name="description" content="'+esc(d)+'">\\n';
      if(c) s+='<link rel="canonical" href="'+esc(c)+'">\\n';
      if(rb) s+='<meta name="robots" content="'+esc(rb)+'">\\n';
      if(t) s+='<meta property="og:title" content="'+esc(t)+'">\\n';
      if(d) s+='<meta property="og:description" content="'+esc(d)+'">\\n';
      if(c) s+='<meta property="og:url" content="'+esc(c)+'">\\n';
      if(og) s+='<meta property="og:image" content="'+esc(og)+'">\\n';
      if(t) s+='<meta name="twitter:title" content="'+esc(t)+'">\\n';
      if(d) s+='<meta name="twitter:description" content="'+esc(d)+'">\\n';
      if(og) s+='<meta name="twitter:image" content="'+esc(og)+'">\\n';
      s+='<meta name="twitter:card" content="summary_large_image">';
      out.textContent=s;
    }
    ids.forEach(function(e){e.addEventListener('input',r);}); r();
    document.getElementById('mt-copy').addEventListener('click',function(){navigator.clipboard.writeText(out.textContent);});
  })();
</script>
"""


def _serp_snippet_preview():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Page URL <input id="sn-url" value="https://shahababbasi.com/" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Title (50-60) <input id="sn-title" maxlength="80" value="Free SEO Tools" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Meta description (140-160) <textarea id="sn-desc" rows="3" maxlength="200">Browser-based SEO tools, no signup, instant results.</textarea></label>
  </form>
  <div class="glass-strong p-5 rounded-lg">
    <p class="text-xs text-foreground/60" id="sn-prev-url">https://shahababbasi.com/</p>
    <h3 id="sn-prev-title" class="text-lg text-blue-400 mt-1">Free SEO Tools</h3>
    <p id="sn-prev-desc" class="mt-1 text-sm text-foreground/80">Browser-based SEO tools, no signup, instant results.</p>
    <p id="sn-meter" class="mt-3 text-xs text-foreground/60"></p>
  </div>
</div>
<script>
  (function(){
    var u=document.getElementById('sn-url'),t=document.getElementById('sn-title'),d=document.getElementById('sn-desc');
    function r(){
      document.getElementById('sn-prev-url').textContent=u.value||'https://example.com/';
      document.getElementById('sn-prev-title').textContent=t.value||'Page title';
      document.getElementById('sn-prev-desc').textContent=d.value||'Page description';
      var msg='';
      if(t.value.length>60) msg+='Title too long. ';
      if(t.value.length<30) msg+='Title may be too short. ';
      if(d.value.length>160) msg+='Description too long. ';
      if(d.value.length<120) msg+='Description may be too short. ';
      if(!msg) msg='Length looks good for SERPs.';
      document.getElementById('sn-meter').textContent=msg+' Title '+t.value.length+'/60. Desc '+d.value.length+'/160.';
    }
    [u,t,d].forEach(function(e){e.addEventListener('input',r);}); r();
  })();
</script>
"""


def _keyword_density():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste your content</label>
  <textarea id="kd-text" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <div class="mt-4 overflow-x-auto">
    <table class="w-full text-sm">
      <thead><tr class="text-left"><th>Word</th><th>Count</th><th>Density</th></tr></thead>
      <tbody id="kd-out"></tbody>
    </table>
  </div>
</div>
<script>
  (function(){
    var ta = document.getElementById('kd-text'), out = document.getElementById('kd-out');
    function run(){
      var stop = new Set(['the','a','an','of','to','and','in','for','on','is','at','it','as','with','by','that','this','from','or','be','are','was','were','will','can','i','you','we','our','your']);
      var words = (ta.value.toLowerCase().match(/[a-z][a-z']+/g) || []);
      var total = words.length;
      var counts = {};
      words.forEach(function(w){ if (stop.has(w)) return; counts[w] = (counts[w]||0)+1; });
      var arr = Object.entries(counts).sort(function(a,b){return b[1]-a[1];}).slice(0,15);
      out.innerHTML = arr.map(function(x){ return '<tr class="border-t border-border/30"><td class="py-1">'+x[0]+'</td><td>'+x[1]+'</td><td>'+(total?(x[1]/total*100).toFixed(2):0)+'%</td></tr>'; }).join('');
    }
    ta.addEventListener('input', run); run();
  })();
</script>
"""


def _robots_txt():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>User-agent <input id="rb-ua" value="*" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Disallow paths (one per line) <textarea id="rb-dis" rows="4" class="rounded-lg bg-card/60 border border-border px-3 py-2">/admin/
/private/</textarea></label>
    <label>Allow paths (one per line, optional) <textarea id="rb-allow" rows="2" class="rounded-lg bg-card/60 border border-border px-3 py-2"></textarea></label>
    <label>Sitemap URL <input id="rb-sm" placeholder="https://example.com/sitemap.xml" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Crawl-delay (optional) <input id="rb-cd" type="number" placeholder="0" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
  </form>
  <div>
    <p class="font-display font-semibold mb-2 text-sm">Generated robots.txt</p>
    <pre id="rb-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg"></pre>
    <button id="rb-copy" class="mt-3 inline-flex rounded-xl border border-border/60 px-4 py-2 text-sm hover:bg-white/5">Copy</button>
  </div>
</div>
<script>
  (function(){
    var ua=document.getElementById('rb-ua'),dis=document.getElementById('rb-dis'),al=document.getElementById('rb-allow'),sm=document.getElementById('rb-sm'),cd=document.getElementById('rb-cd'),o=document.getElementById('rb-out');
    function r(){
      var s='User-agent: '+(ua.value||'*')+'\\n';
      (dis.value.split('\\n')).forEach(function(p){ if(p.trim()) s+='Disallow: '+p.trim()+'\\n'; });
      (al.value.split('\\n')).forEach(function(p){ if(p.trim()) s+='Allow: '+p.trim()+'\\n'; });
      if(cd.value) s+='Crawl-delay: '+cd.value+'\\n';
      if(sm.value) s+='\\nSitemap: '+sm.value+'\\n';
      o.textContent=s;
    }
    [ua,dis,al,sm,cd].forEach(function(e){e.addEventListener('input',r);}); r();
    document.getElementById('rb-copy').addEventListener('click',function(){navigator.clipboard.writeText(o.textContent);});
  })();
</script>
"""


def _roas_calculator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Revenue ($) <input type="number" id="ro-rev" placeholder="10000" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Ad spend ($) <input type="number" id="ro-spend" placeholder="2500" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
  </form>
  <div class="glass-strong p-4 rounded-lg">
    <p class="text-xs text-foreground/60">ROAS</p>
    <p id="ro-out" class="font-display text-3xl">0.00x</p>
    <p id="ro-out2" class="mt-2 text-sm text-foreground/70"></p>
  </div>
</div>
<script>
  (function(){
    function r(){
      var rev=parseFloat(document.getElementById('ro-rev').value)||0;
      var sp=parseFloat(document.getElementById('ro-spend').value)||0;
      var v = sp ? (rev/sp) : 0;
      document.getElementById('ro-out').textContent = v.toFixed(2) + 'x';
      var st = v >= 4 ? 'Excellent' : v >= 2 ? 'Good' : v >= 1 ? 'Break-even' : 'Underperforming';
      document.getElementById('ro-out2').textContent = st + '. Profit: $' + (rev - sp).toFixed(2);
    }
    ['ro-rev','ro-spend'].forEach(function(id){document.getElementById(id).addEventListener('input',r);}); r();
  })();
</script>
"""


# =============================================================================
# Bulk tools (already fixed for popup-blocker - copy from generate.py)
# =============================================================================


def _bulk_index_checker():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">URLs to Check (one per line)</label>
  <textarea id="bic-urls" rows="8" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 outline-none focus:ring-2 focus:ring-primary text-sm" placeholder="https://example.com/page-1
https://example.com/page-2
example.com/blog/post-title
..."></textarea>
  <p id="bic-count" class="mt-1 text-xs text-foreground/60">0 URLs entered</p>
  <div class="mt-4 flex flex-wrap items-center gap-3">
    <button id="bic-go" class="rounded-xl bg-gradient-brand px-5 py-3 text-sm font-medium shadow-glow-primary">Check 0 URLs</button>
    <button id="bic-openall" class="rounded-xl border border-border/60 px-4 py-3 text-sm hidden">Open all in tabs</button>
    <button id="bic-copy" class="rounded-xl border border-border/60 px-4 py-3 text-sm hidden">Copy queries</button>
    <button id="bic-clear" class="rounded-xl border border-border/60 px-4 py-3 text-sm hidden">Clear</button>
  </div>
  <div id="bic-out" class="mt-5 hidden">
    <p class="text-sm font-display font-semibold mb-2">site: search links</p>
    <ul id="bic-list" class="glass-strong rounded-lg p-3 max-h-80 overflow-auto space-y-2 text-sm"></ul>
    <p class="mt-3 text-xs text-foreground/60">Click any link to open that site: search in a new tab. Use "Open all in tabs" to open every link at once (allow popups for this page on first run).</p>
  </div>
</div>
<script>
  (function(){
    var ta=document.getElementById('bic-urls'),count=document.getElementById('bic-count'),btn=document.getElementById('bic-go'),openAll=document.getElementById('bic-openall'),copyBtn=document.getElementById('bic-copy'),clearBtn=document.getElementById('bic-clear'),outBox=document.getElementById('bic-out'),listEl=document.getElementById('bic-list');
    function urls(){return (ta.value||'').split(/\\r?\\n/).map(function(s){return s.trim();}).filter(Boolean);}
    function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
    function update(){var n=urls().length; count.textContent=n+' URLs entered'; btn.textContent='Check '+n+' URLs'; btn.disabled=n===0;}
    ta.addEventListener('input',update); update();
    function buildSearch(raw){var u=raw.replace(/^https?:\\/\\//,'').replace(/\\/$/,''); return {domain:u, search:'https://www.google.com/search?q=site%3A'+encodeURIComponent(u)};}
    function render(items){listEl.innerHTML=''; items.forEach(function(it,i){var li=document.createElement('li'); li.className='flex items-center justify-between gap-3 glass p-2 rounded-md'; li.innerHTML='<span class="text-foreground/70 text-xs shrink-0">'+(i+1)+'.</span><span class="flex-1 truncate font-mono text-xs">site:'+esc(it.domain)+'</span><a href="'+it.search+'" target="_blank" rel="noopener" class="text-accent text-xs underline shrink-0">Open</a>'; listEl.appendChild(li);}); outBox.classList.remove('hidden'); openAll.classList.remove('hidden'); copyBtn.classList.remove('hidden'); clearBtn.classList.remove('hidden');}
    btn.addEventListener('click',function(){var list=urls(); if(!list.length) return; var items=list.map(buildSearch); render(items); items.forEach(function(it){window.open(it.search,'_blank','noopener');});});
    openAll.addEventListener('click',function(){var list=urls(); if(!list.length) return; list.map(buildSearch).forEach(function(it){window.open(it.search,'_blank','noopener');});});
    copyBtn.addEventListener('click',function(){var list=urls().map(buildSearch).map(function(it){return it.search;}).join('\\n'); navigator.clipboard.writeText(list); copyBtn.textContent='Copied'; setTimeout(function(){copyBtn.textContent='Copy queries';},1500);});
    clearBtn.addEventListener('click',function(){ta.value=''; update(); listEl.innerHTML=''; outBox.classList.add('hidden'); openAll.classList.add('hidden'); copyBtn.classList.add('hidden'); clearBtn.classList.add('hidden');});
  })();
</script>
"""


def _bulk_keyword_checker():
    return """
<div class="glass p-6 grid lg:grid-cols-2 gap-6">
  <div>
    <p class="text-sm font-display font-semibold mb-2">Enter Keywords</p>
    <div class="grid sm:grid-cols-2 gap-3 text-sm">
      <label><span class="block font-display font-semibold">Business Name</span><input id="bkc-brand" placeholder="Your Brand Name" class="mt-1 w-full h-11 rounded-lg bg-card/60 border border-border px-3"><span class="block mt-1 text-xs text-foreground/60">Auto-highlight in search results</span></label>
      <label><span class="block font-display font-semibold">Website URL</span><input id="bkc-site" placeholder="yourbrand.com" class="mt-1 w-full h-11 rounded-lg bg-card/60 border border-border px-3"><span class="block mt-1 text-xs text-foreground/60">For tracking reference</span></label>
    </div>
    <label class="block mt-3 text-sm"><span class="block font-display font-semibold">Domain to Check (optional)</span><input id="bkc-domain" placeholder="example.com" class="mt-1 w-full h-11 rounded-lg bg-card/60 border border-border px-3"><span class="block mt-1 text-xs text-foreground/60">Add site: filter to search</span></label>
    <label class="block mt-3 text-sm"><span class="block font-display font-semibold">Keywords (one per line)</span><textarea id="bkc-kws" rows="6" placeholder="keyword 1
keyword 2
keyword 3" class="mt-1 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea><span id="bkc-count" class="block mt-1 text-xs text-foreground/60">0 keywords entered</span></label>
    <div class="grid sm:grid-cols-2 gap-3 text-sm mt-3">
      <label><span class="block font-display font-semibold">Location / City (optional)</span><input id="bkc-loc" placeholder="e.g. dallas, london" class="mt-1 w-full h-11 rounded-lg bg-card/60 border border-border px-3"></label>
      <label><span class="block font-display font-semibold">Language Code (optional)</span><input id="bkc-lang" placeholder="e.g. en, es, de" class="mt-1 w-full h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    </div>
    <div class="mt-4 flex flex-wrap gap-3">
      <button id="bkc-gen" class="rounded-xl bg-gradient-brand px-5 py-3 text-sm font-medium shadow-glow-primary">Generate Links</button>
      <button id="bkc-open" class="rounded-xl border border-border/60 px-4 py-3 text-sm hidden">Open all in tabs</button>
      <button id="bkc-copy" class="rounded-xl border border-border/60 px-4 py-3 text-sm hidden">Copy all</button>
    </div>
  </div>
  <div>
    <p class="text-sm font-display font-semibold mb-2">Search Links</p>
    <div id="bkc-out" class="glass-strong rounded-lg p-4 min-h-[12rem] text-sm">
      <p class="text-foreground/60 text-center mt-12">Enter keywords and click "Generate Links" to start</p>
    </div>
  </div>
</div>
<script>
  (function(){
    var brand=document.getElementById('bkc-brand'),site=document.getElementById('bkc-site'),dom=document.getElementById('bkc-domain'),kws=document.getElementById('bkc-kws'),loc=document.getElementById('bkc-loc'),lang=document.getElementById('bkc-lang'),gen=document.getElementById('bkc-gen'),openAll=document.getElementById('bkc-open'),copyAll=document.getElementById('bkc-copy'),out=document.getElementById('bkc-out'),count=document.getElementById('bkc-count');
    function list(){return (kws.value||'').split(/\\r?\\n/).map(function(s){return s.trim();}).filter(Boolean);}
    function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
    function update(){count.textContent=list().length+' keywords entered';}
    kws.addEventListener('input',update); update();
    function buildQuery(kw){var parts=[kw]; if(dom.value) parts.push('site:'+dom.value.replace(/^https?:\\/\\//,'')); if(loc.value) parts.push(loc.value); var q=parts.join(' '); var u='https://www.google.com/search?q='+encodeURIComponent(q); if(lang.value) u+='&hl='+encodeURIComponent(lang.value); if(loc.value && /^[a-z]{2}$/i.test(loc.value.trim())) u+='&gl='+encodeURIComponent(loc.value.trim().toLowerCase()); return u;}
    gen.addEventListener('click',function(){var arr=list(); if(!arr.length) return; var html='<ul class="space-y-2">'; var urls=[]; arr.forEach(function(kw){var u=buildQuery(kw); urls.push(u); var label=brand.value?esc(kw)+' <span class="text-foreground/50">(brand: '+esc(brand.value)+')</span>':esc(kw); html+='<li class="glass p-3 flex items-center justify-between gap-3"><span>'+label+'</span><a target="_blank" rel="noopener" class="text-accent text-xs underline" href="'+u+'">Open</a></li>';}); html+='</ul>'; if(site.value) html+='<p class="mt-3 text-xs text-foreground/60">Reference: '+esc(site.value)+'</p>'; out.innerHTML=html; openAll.classList.remove('hidden'); copyAll.classList.remove('hidden'); openAll.onclick=function(){urls.forEach(function(u){window.open(u,'_blank','noopener');});}; copyAll.onclick=function(){navigator.clipboard.writeText(urls.join('\\n')); copyAll.textContent='Copied'; setTimeout(function(){copyAll.textContent='Copy all';},1500);};});
  })();
</script>
"""


# =============================================================================
# Schema generators - produce JSON-LD for any schema.org type
# =============================================================================


def _schema_generator(slug: str, name: str):
    # Determine schema type from slug
    type_map = {
        "ai-schema-generator": "WebSite",
        "article-schema-generator": "Article",
        "breadcrumb-schema-generator": "BreadcrumbList",
        "ecommerce-schema-generator": "Product",
        "event-schema-generator": "Event",
        "faq-schema-generator": "FAQPage",
        "howto-schema-generator": "HowTo",
        "local-schema-generator": "LocalBusiness",
        "localbusiness-schema-generator": "LocalBusiness",
        "product-schema-generator": "Product",
        "review-schema-generator": "Review",
        "videoobject-schema-generator": "VideoObject",
        "schema-generator": "Article",
    }
    schema_type = type_map.get(slug, "Article")

    examples = {
        "Article": '{"headline":"Page title","author":"Shahab Abbasi","datePublished":"2026-01-01","image":"https://example.com/og.png"}',
        "FAQPage": '{"mainEntity":[{"@type":"Question","name":"Q1","acceptedAnswer":{"@type":"Answer","text":"A1"}}]}',
        "HowTo": '{"name":"How to X","step":[{"@type":"HowToStep","text":"Step 1"},{"@type":"HowToStep","text":"Step 2"}]}',
        "Product": '{"name":"Product name","description":"Description","sku":"ABC-123","brand":"Brand","offers":{"@type":"Offer","price":"19.99","priceCurrency":"USD"}}',
        "Event": '{"name":"Event name","startDate":"2026-06-01T10:00","location":{"@type":"Place","name":"Venue","address":"City"}}',
        "Review": '{"itemReviewed":{"@type":"Thing","name":"Item"},"reviewRating":{"@type":"Rating","ratingValue":"5"},"author":"Reviewer name","reviewBody":"Review text"}',
        "LocalBusiness": '{"name":"Business","telephone":"+1-555-0000","address":{"@type":"PostalAddress","streetAddress":"123 Main","addressLocality":"City","addressCountry":"US"}}',
        "BreadcrumbList": '{"itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://example.com/"},{"@type":"ListItem","position":2,"name":"Page","item":"https://example.com/page"}]}',
        "VideoObject": '{"name":"Video title","description":"Description","thumbnailUrl":"https://example.com/thumb.jpg","uploadDate":"2026-01-01","contentUrl":"https://example.com/video.mp4"}',
        "WebSite": '{"name":"Site name","url":"https://example.com","potentialAction":{"@type":"SearchAction","target":"https://example.com/search?q={search_term_string}","query-input":"required name=search_term_string"}}',
    }
    example = examples.get(schema_type, '{"name":"Page title"}')

    return f"""
<div class="glass p-6">
  <p class="text-sm">Paste your data as JSON. Output is valid JSON-LD ready to drop in your &lt;head&gt;.</p>
  <div class="mt-3 grid md:grid-cols-2 gap-4">
    <div>
      <label class="text-xs text-foreground/60">Schema type</label>
      <input id="sg-type" value="{schema_type}" class="mt-1 h-11 w-full rounded-lg bg-card/60 border border-border px-3 text-sm">
      <label class="text-xs text-foreground/60 mt-3 block">Properties (JSON)</label>
      <textarea id="sg-input" rows="10" class="mt-1 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-xs font-mono">{example}</textarea>
      <button id="sg-go" class="mt-3 inline-flex rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate JSON-LD</button>
      <button id="sg-copy" class="mt-3 ml-2 inline-flex rounded-xl border border-border/60 px-4 py-2 text-sm">Copy</button>
    </div>
    <div>
      <label class="text-xs text-foreground/60">JSON-LD output</label>
      <pre id="sg-out" class="mt-1 text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
    </div>
  </div>
</div>
<script>
  (function(){{
    var go=document.getElementById('sg-go'),copy=document.getElementById('sg-copy'),inp=document.getElementById('sg-input'),typ=document.getElementById('sg-type'),out=document.getElementById('sg-out');
    function r(){{
      var raw=inp.value||'{{}}';
      var data; try{{ data=JSON.parse(raw); }}catch(e){{ out.textContent='Invalid JSON: '+e.message; return; }}
      var schema={{ '@context':'https://schema.org', '@type':typ.value||'Thing' }};
      Object.keys(data).forEach(function(k){{ schema[k]=data[k]; }});
      out.textContent='<script type="application/ld+json">\\n'+JSON.stringify(schema,null,2)+'\\n<\\/script>';
    }}
    go.addEventListener('click',r); r();
    copy.addEventListener('click',function(){{navigator.clipboard.writeText(out.textContent); copy.textContent='Copied'; setTimeout(function(){{copy.textContent='Copy';}},1500);}});
  }})();
</script>
"""


def _json_ld_validator():
    return """
<div class="glass p-6">
  <p class="text-sm">Paste any JSON-LD block (with or without &lt;script&gt; tags). The validator parses and reports common issues.</p>
  <textarea id="jv-input" rows="10" class="mt-3 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-xs font-mono" placeholder='{"@context":"https://schema.org","@type":"Article","headline":"..."}'></textarea>
  <button id="jv-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Validate</button>
  <pre id="jv-out" class="mt-4 text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg"></pre>
</div>
<script>
  (function(){
    var inp=document.getElementById('jv-input'),go=document.getElementById('jv-go'),out=document.getElementById('jv-out');
    function v(){
      var raw=(inp.value||'').replace(/<script[^>]*>|<\\/script>/g,'').trim();
      var data; try{ data=JSON.parse(raw);}catch(e){ out.textContent='INVALID: '+e.message; return; }
      var arr=Array.isArray(data)?data:[data]; var msgs=[]; var ok=true;
      arr.forEach(function(d,i){
        if(!d['@context']) { msgs.push('['+i+'] missing @context'); ok=false; }
        if(!d['@type']) { msgs.push('['+i+'] missing @type'); ok=false; }
        if(d['@context'] && !/schema\\.org/.test(d['@context'])) { msgs.push('['+i+'] @context should reference schema.org'); }
        if(d['@type']==='Article' && !d.headline) { msgs.push('['+i+'] Article missing headline'); }
        if(d['@type']==='FAQPage' && !d.mainEntity) { msgs.push('['+i+'] FAQPage missing mainEntity'); }
        if(d['@type']==='Product' && !d.name) { msgs.push('['+i+'] Product missing name'); }
        if(d['@type']==='Product' && !d.offers) { msgs.push('['+i+'] Product missing offers'); }
        if(d['@type']==='Event' && !d.startDate) { msgs.push('['+i+'] Event missing startDate'); }
      });
      out.textContent=(ok?'PARSED OK ('+arr.length+' object'+(arr.length>1?'s':'')+').':'PARSED with issues.')+'\\n\\n'+(msgs.length?msgs.join('\\n'):'No issues detected.')+'\\n\\nFormatted:\\n'+JSON.stringify(data,null,2);
    }
    go.addEventListener('click',v);
  })();
</script>
"""


# =============================================================================
# Calculators (live recalc on input)
# =============================================================================


def _generic_calc(fields, formula_js, output_label, format_js="v.toFixed(2)"):
    """fields: list of (id, label, default, type) tuples. formula_js: JS that uses the field IDs and assigns to var v."""
    field_html = "\n".join([
        f'<label class="block text-sm"><span class="block font-display font-semibold">{label}</span><input type="{typ}" id="{fid}" value="{default}" class="mt-1 w-full h-11 rounded-lg bg-card/60 border border-border px-3"></label>'
        for fid, label, default, typ in fields
    ])
    field_ids = [fid for fid, _, _, _ in fields]
    listeners = ",".join([f"'{i}'" for i in field_ids])
    return f"""
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">{field_html}</form>
  <div class="glass-strong p-5 rounded-lg flex flex-col justify-center">
    <p class="text-xs text-foreground/60">{output_label}</p>
    <p id="calc-out" class="font-display text-3xl mt-1">-</p>
    <p id="calc-out2" class="mt-2 text-sm text-foreground/70"></p>
  </div>
</div>
<script>
  (function(){{
    function num(id){{var v=parseFloat(document.getElementById(id).value); return isFinite(v)?v:0;}}
    function r(){{
      try {{ {formula_js}; document.getElementById('calc-out').textContent={format_js}; }} catch(e){{ document.getElementById('calc-out').textContent='-'; }}
    }}
    [{listeners}].forEach(function(id){{var el=document.getElementById(id); if(el) el.addEventListener('input',r);}}); r();
  }})();
</script>
"""


def _cpc_calculator():
    return _generic_calc(
        [("cpc-cost", "Total cost ($)", "100", "number"), ("cpc-clicks", "Total clicks", "50", "number")],
        "var cost=num('cpc-cost'),clicks=num('cpc-clicks'); var v=clicks?(cost/clicks):0; document.getElementById('calc-out2').textContent='Spend per click for '+clicks+' clicks at $'+cost.toFixed(2)+' total.'",
        "Cost per click", "'$'+v.toFixed(2)",
    )


def _ctr_calculator():
    return _generic_calc(
        [("ctr-cl", "Clicks", "120", "number"), ("ctr-im", "Impressions", "5000", "number")],
        "var c=num('ctr-cl'),i=num('ctr-im'); var v=i?(c/i*100):0; document.getElementById('calc-out2').textContent='Industry avg: 1.91% (search), 0.46% (display).'",
        "Click-through rate", "v.toFixed(2)+'%'",
    )


def _ab_test_duration():
    return _generic_calc(
        [
            ("ab-vis", "Visitors per day", "1000", "number"),
            ("ab-base", "Baseline conversion (%)", "2.0", "number"),
            ("ab-mde", "Minimum detectable effect (%)", "0.5", "number"),
        ],
        "var vis=num('ab-vis'),base=num('ab-base')/100,mde=num('ab-mde')/100; var sample=Math.ceil(16*base*(1-base)/(mde*mde)); var v=Math.max(1,Math.ceil(sample*2/vis)); document.getElementById('calc-out2').textContent='~'+sample.toLocaleString()+' visitors per variant. 95% confidence, 80% power.'",
        "Days to reach significance", "v + ' days'",
    )


def _seo_roi():
    return _generic_calc(
        [
            ("roi-tr", "Monthly organic traffic", "5000", "number"),
            ("roi-cv", "Conversion rate (%)", "2.0", "number"),
            ("roi-aov", "Average order value ($)", "150", "number"),
            ("roi-cost", "Monthly SEO cost ($)", "3000", "number"),
        ],
        "var tr=num('roi-tr'),cv=num('roi-cv')/100,aov=num('roi-aov'),cost=num('roi-cost'); var rev=tr*cv*aov; var v=cost?((rev-cost)/cost*100):0; document.getElementById('calc-out2').textContent='Monthly revenue: $'+rev.toFixed(0)+'. Profit: $'+(rev-cost).toFixed(0)+'.'",
        "ROI", "v.toFixed(0)+'%'",
    )


def _traffic_forecaster():
    return _generic_calc(
        [
            ("tf-vol", "Monthly search volume", "10000", "number"),
            ("tf-pos", "Target ranking position", "3", "number"),
        ],
        ("var vol=num('tf-vol'),pos=num('tf-pos'); var ctr={1:0.396,2:0.187,3:0.103,4:0.072,5:0.052,6:0.039,7:0.030,8:0.024,9:0.020,10:0.017}[Math.max(1,Math.min(10,Math.round(pos)))]||0.012; var v=Math.round(vol*ctr); "
         "document.getElementById('calc-out2').textContent='Estimated CTR at position '+pos+': '+(ctr*100).toFixed(1)+'%. Source: 2024 click-through studies.'"),
        "Estimated monthly traffic", "v.toLocaleString()+' visits'",
    )


def _ads_budget():
    return _generic_calc(
        [
            ("gb-cpc", "Target CPC ($)", "2.50", "number"),
            ("gb-cl", "Clicks per day", "50", "number"),
            ("gb-d", "Days", "30", "number"),
        ],
        "var cpc=num('gb-cpc'),cl=num('gb-cl'),d=num('gb-d'); var v=cpc*cl*d; document.getElementById('calc-out2').textContent='Daily: $'+(cpc*cl).toFixed(2)+'. Monthly clicks: '+(cl*d).toLocaleString()+'.'",
        "Total budget", "'$'+v.toLocaleString()",
    )


def _quality_score_estimator():
    return _generic_calc(
        [
            ("qs-ctr", "Expected CTR (1-10)", "7", "number"),
            ("qs-rel", "Ad relevance (1-10)", "8", "number"),
            ("qs-lp", "Landing page experience (1-10)", "8", "number"),
        ],
        "var v=Math.min(10,Math.max(1,Math.round((num('qs-ctr')+num('qs-rel')+num('qs-lp'))/3))); document.getElementById('calc-out2').textContent='Higher Quality Score = lower CPC + better ad position.'",
        "Estimated Quality Score", "v + '/10'",
    )


def _website_cost():
    return _generic_calc(
        [
            ("wc-pages", "Number of pages", "10", "number"),
            ("wc-ppage", "Cost per page ($)", "150", "number"),
            ("wc-extras", "Extras (CMS, e-com, custom features) ($)", "1500", "number"),
        ],
        "var v=num('wc-pages')*num('wc-ppage')+num('wc-extras'); document.getElementById('calc-out2').textContent='Pages: $'+(num('wc-pages')*num('wc-ppage')).toFixed(0)+'. Extras: $'+num('wc-extras').toFixed(0)+'.'",
        "Estimated total cost", "'$'+v.toLocaleString()",
    )


def _da_estimator():
    return _generic_calc(
        [
            ("da-bl", "Total backlinks", "500", "number"),
            ("da-rd", "Referring domains", "75", "number"),
            ("da-age", "Domain age (years)", "3", "number"),
        ],
        "var bl=num('da-bl'),rd=num('da-rd'),age=num('da-age'); var v=Math.min(100,Math.round(Math.log10(rd+1)*15+Math.log10(bl+1)*5+Math.min(20,age*2))); document.getElementById('calc-out2').textContent='Heuristic estimate. For a precise score check Moz, Ahrefs, or SEMrush.'",
        "Estimated Domain Authority", "v + '/100'",
    )


def _crawl_budget():
    return _generic_calc(
        [
            ("cb-pages", "Indexable pages", "5000", "number"),
            ("cb-freq", "Updates per week", "20", "number"),
            ("cb-rate", "Pages crawled per second (Googlebot)", "1", "number"),
        ],
        "var p=num('cb-pages'),f=num('cb-freq'),r=num('cb-rate'); var v=Math.ceil(p/(r*86400)); document.getElementById('calc-out2').textContent='With '+f+' updates/week, prioritize internal linking on the most-changed sections.'",
        "Days to crawl every page once", "v + ' days'",
    )


def _speed_to_conversion():
    return _generic_calc(
        [
            ("ps-cur", "Current LCP (seconds)", "4.0", "number"),
            ("ps-target", "Target LCP (seconds)", "2.5", "number"),
            ("ps-cv", "Current conversion (%)", "2.0", "number"),
        ],
        "var cur=num('ps-cur'),tgt=num('ps-target'),cv=num('ps-cv'); var diff=cur-tgt; var lift=Math.max(0,diff*7); var v=cv*(1+lift/100); document.getElementById('calc-out2').textContent='Each second of LCP reduction lifts conversion by ~7% (Google). Saved: '+diff.toFixed(1)+'s.'",
        "Projected conversion rate", "v.toFixed(2)+'%'",
    )


def _cpc_savings():
    return _generic_calc(
        [
            ("cs-cur", "Current CPC ($)", "5.00", "number"),
            ("cs-new", "New CPC after QS lift ($)", "3.50", "number"),
            ("cs-cl", "Clicks per month", "1000", "number"),
        ],
        "var cur=num('cs-cur'),nw=num('cs-new'),cl=num('cs-cl'); var v=(cur-nw)*cl; document.getElementById('calc-out2').textContent='Annual savings: $'+(v*12).toLocaleString()+'.'",
        "Monthly savings", "'$'+v.toLocaleString()",
    )


def _pipeline_attribution():
    return _generic_calc(
        [
            ("pa-tr", "Monthly traffic", "10000", "number"),
            ("pa-lcv", "Lead conversion (%)", "2.0", "number"),
            ("pa-mqlcv", "MQL-to-SQL (%)", "30", "number"),
            ("pa-acv", "Average deal size ($)", "5000", "number"),
        ],
        "var tr=num('pa-tr'),lcv=num('pa-lcv')/100,mql=num('pa-mqlcv')/100,acv=num('pa-acv'); var leads=tr*lcv,sqls=leads*mql; var v=sqls*acv; document.getElementById('calc-out2').textContent='Leads: '+leads.toFixed(0)+'. SQLs: '+sqls.toFixed(0)+'.'",
        "Pipeline value", "'$'+v.toLocaleString()",
    )


def _crawl_stats_estimator():
    return _crawl_budget()


# =============================================================================
# Text/code utilities
# =============================================================================


def _slug_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Page title or text</label>
    <textarea id="sl-input" rows="6" placeholder="Type your title here..." class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
    <div class="mt-3 grid grid-cols-2 gap-3 text-xs">
      <label class="flex items-center gap-2"><input type="checkbox" id="sl-sw" checked> Strip stop words</label>
      <label class="flex items-center gap-2"><input type="checkbox" id="sl-num"> Strip numbers</label>
    </div>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">URL slug</p>
    <input id="sl-out" readonly class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
    <button id="sl-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy slug</button>
    <p class="mt-3 text-xs text-foreground/60">Slug rules: lowercase, hyphens between words, ASCII only, under 60 chars when possible.</p>
  </div>
</div>
<script>
  (function(){
    var inp=document.getElementById('sl-input'),sw=document.getElementById('sl-sw'),nm=document.getElementById('sl-num'),out=document.getElementById('sl-out');
    var stop=new Set(['the','a','an','and','or','to','of','in','for','on','with','by','from','as','at']);
    function r(){
      var s=(inp.value||'').toLowerCase().normalize('NFKD').replace(/[\\u0300-\\u036f]/g,'');
      s=s.replace(/[^a-z0-9\\s-]/g,' ').trim();
      var parts=s.split(/\\s+/).filter(Boolean);
      if(sw.checked) parts=parts.filter(function(p){return !stop.has(p);});
      if(nm.checked) parts=parts.filter(function(p){return !/^\\d+$/.test(p);});
      out.value=parts.join('-').replace(/-+/g,'-');
    }
    [inp,sw,nm].forEach(function(e){e.addEventListener('input',r); e.addEventListener('change',r);}); r();
    document.getElementById('sl-copy').addEventListener('click',function(){navigator.clipboard.writeText(out.value); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy slug';},1500);});
  })();
</script>
"""


def _utm_builder():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Destination URL <input id="utm-url" placeholder="https://example.com/landing" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>utm_source <input id="utm-src" placeholder="newsletter" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>utm_medium <input id="utm-med" placeholder="email" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>utm_campaign <input id="utm-cmp" placeholder="spring-sale" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>utm_term (optional) <input id="utm-term" placeholder="seo+services" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>utm_content (optional) <input id="utm-cnt" placeholder="cta-button" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
  </form>
  <div>
    <p class="font-display font-semibold mb-2 text-sm">Tagged URL</p>
    <textarea id="utm-out" rows="4" readonly class="w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-xs font-mono"></textarea>
    <button id="utm-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy URL</button>
  </div>
</div>
<script>
  (function(){
    var ids=['utm-url','utm-src','utm-med','utm-cmp','utm-term','utm-cnt'].map(function(i){return document.getElementById(i);});
    var out=document.getElementById('utm-out');
    function r(){
      var url=ids[0].value; if(!url){out.value='';return;}
      var params=[];
      ['source','medium','campaign','term','content'].forEach(function(k,i){
        var v=ids[i+1].value.trim(); if(v) params.push('utm_'+k+'='+encodeURIComponent(v));
      });
      var sep=url.indexOf('?')>=0?'&':'?';
      out.value=params.length?url+sep+params.join('&'):url;
    }
    ids.forEach(function(e){e.addEventListener('input',r);}); r();
    document.getElementById('utm-copy').addEventListener('click',function(){navigator.clipboard.writeText(out.value); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy URL';},1500);});
  })();
</script>
"""


def _url_encoder_decoder():
    return _encoder_pair("URL", "encodeURIComponent", "decodeURIComponent", "Hello world?foo=bar&baz=qux", "url-encode")


def _html_encoder_decoder():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Plain text / HTML</label>
    <textarea id="he-plain" rows="8" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono">&lt;p&gt;Hello "world" &amp; co.&lt;/p&gt;</textarea>
  </div>
  <div>
    <label class="text-sm font-display font-semibold">Encoded / decoded</label>
    <textarea id="he-enc" rows="8" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
    <div class="mt-3 flex gap-2">
      <button id="he-do-enc" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Encode &gt;</button>
      <button id="he-do-dec" class="rounded-xl border border-border/60 px-4 py-2 text-sm">&lt; Decode</button>
    </div>
  </div>
</div>
<script>
  (function(){
    var p=document.getElementById('he-plain'),e=document.getElementById('he-enc');
    document.getElementById('he-do-enc').addEventListener('click',function(){
      e.value=(p.value||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
    });
    document.getElementById('he-do-dec').addEventListener('click',function(){
      var t=document.createElement('textarea'); t.innerHTML=e.value||''; p.value=t.value;
    });
  })();
</script>
"""


def _encoder_pair(label, encoder, decoder, default, prefix):
    return f"""
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Plain text</label>
    <textarea id="{prefix}-plain" rows="8" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono">{default}</textarea>
  </div>
  <div>
    <label class="text-sm font-display font-semibold">Encoded / decoded {label}</label>
    <textarea id="{prefix}-enc" rows="8" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
    <div class="mt-3 flex gap-2">
      <button id="{prefix}-do-enc" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Encode &gt;</button>
      <button id="{prefix}-do-dec" class="rounded-xl border border-border/60 px-4 py-2 text-sm">&lt; Decode</button>
    </div>
  </div>
</div>
<script>
  (function(){{
    var p=document.getElementById('{prefix}-plain'),e=document.getElementById('{prefix}-enc');
    document.getElementById('{prefix}-do-enc').addEventListener('click',function(){{
      try{{ e.value={encoder}(p.value||''); }}catch(err){{ e.value='Error: '+err.message; }}
    }});
    document.getElementById('{prefix}-do-dec').addEventListener('click',function(){{
      try{{ p.value={decoder}(e.value||''); }}catch(err){{ p.value='Error: '+err.message; }}
    }});
  }})();
</script>
"""


def _text_case_converter():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Input text</label>
  <textarea id="tc-input" rows="6" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <div class="mt-4 flex flex-wrap gap-2">
    <button data-case="upper" class="tc-btn rounded-xl border border-border/60 px-3 py-2 text-xs">UPPERCASE</button>
    <button data-case="lower" class="tc-btn rounded-xl border border-border/60 px-3 py-2 text-xs">lowercase</button>
    <button data-case="title" class="tc-btn rounded-xl border border-border/60 px-3 py-2 text-xs">Title Case</button>
    <button data-case="sentence" class="tc-btn rounded-xl border border-border/60 px-3 py-2 text-xs">Sentence case</button>
    <button data-case="camel" class="tc-btn rounded-xl border border-border/60 px-3 py-2 text-xs">camelCase</button>
    <button data-case="pascal" class="tc-btn rounded-xl border border-border/60 px-3 py-2 text-xs">PascalCase</button>
    <button data-case="snake" class="tc-btn rounded-xl border border-border/60 px-3 py-2 text-xs">snake_case</button>
    <button data-case="kebab" class="tc-btn rounded-xl border border-border/60 px-3 py-2 text-xs">kebab-case</button>
    <button data-case="alt" class="tc-btn rounded-xl border border-border/60 px-3 py-2 text-xs">aLtErNaTiNg</button>
  </div>
  <textarea id="tc-out" rows="6" readonly class="mt-4 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <button id="tc-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy output</button>
</div>
<script>
  (function(){
    var inp=document.getElementById('tc-input'),out=document.getElementById('tc-out');
    function transform(t,c){
      switch(c){
        case 'upper': return t.toUpperCase();
        case 'lower': return t.toLowerCase();
        case 'title': return t.toLowerCase().replace(/\\b\\w/g,function(s){return s.toUpperCase();});
        case 'sentence': return t.toLowerCase().replace(/(^\\s*\\w|[.!?]\\s*\\w)/g,function(s){return s.toUpperCase();});
        case 'camel': var w=t.toLowerCase().split(/\\s+/).filter(Boolean); return w[0]+w.slice(1).map(function(p){return p.charAt(0).toUpperCase()+p.slice(1);}).join('');
        case 'pascal': return t.toLowerCase().split(/\\s+/).filter(Boolean).map(function(p){return p.charAt(0).toUpperCase()+p.slice(1);}).join('');
        case 'snake': return t.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_+|_+$/g,'');
        case 'kebab': return t.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');
        case 'alt': return t.split('').map(function(ch,i){return i%2?ch.toUpperCase():ch.toLowerCase();}).join('');
      }
      return t;
    }
    document.querySelectorAll('.tc-btn').forEach(function(b){b.addEventListener('click',function(){out.value=transform(inp.value,b.dataset.case);});});
    document.getElementById('tc-copy').addEventListener('click',function(){navigator.clipboard.writeText(out.value); this.textContent='Copied'; var bb=this; setTimeout(function(){bb.textContent='Copy output';},1500);});
  })();
</script>
"""


def _title_case_converter():
    return _text_case_converter()


def _lorem_ipsum():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Count <input type="number" id="li-n" value="5" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Unit
      <select id="li-u" class="h-11 rounded-lg bg-card/60 border border-border px-3">
        <option value="paragraphs">Paragraphs</option>
        <option value="sentences">Sentences</option>
        <option value="words">Words</option>
      </select>
    </label>
    <label class="flex items-center gap-2 text-sm"><input id="li-start" type="checkbox" checked> Start with "Lorem ipsum"</label>
    <button id="li-go" class="rounded-xl bg-gradient-brand px-5 py-3 text-sm shadow-glow-primary">Generate</button>
  </form>
  <div>
    <textarea id="li-out" rows="12" readonly class="w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm"></textarea>
    <button id="li-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy</button>
  </div>
</div>
<script>
  (function(){
    var W=('lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure in reprehenderit voluptate velit esse cillum eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum').split(' ');
    function rand(){return W[Math.floor(Math.random()*W.length)];}
    function sentence(){var n=8+Math.floor(Math.random()*12); var s=[]; for(var i=0;i<n;i++) s.push(rand()); s[0]=s[0].charAt(0).toUpperCase()+s[0].slice(1); return s.join(' ')+'.';}
    function paragraph(){var n=4+Math.floor(Math.random()*4); var p=[]; for(var i=0;i<n;i++) p.push(sentence()); return p.join(' ');}
    function gen(){
      var n=Math.max(1,parseInt(document.getElementById('li-n').value,10)||5),u=document.getElementById('li-u').value,start=document.getElementById('li-start').checked;
      var arr=[];
      if(u==='paragraphs') for(var i=0;i<n;i++) arr.push(paragraph());
      if(u==='sentences') for(var j=0;j<n;j++) arr.push(sentence());
      if(u==='words') { var w=[]; for(var k=0;k<n;k++) w.push(rand()); arr.push(w.join(' ')); }
      var out=arr.join(u==='paragraphs'?'\\n\\n':' ');
      if(start && u==='paragraphs') out=out.replace(/^[A-Z][a-z]+/, 'Lorem ipsum');
      if(start && u==='sentences') out='Lorem ipsum dolor sit amet, '+out.toLowerCase();
      document.getElementById('li-out').value=out;
    }
    document.getElementById('li-go').addEventListener('click',gen); gen();
    document.getElementById('li-copy').addEventListener('click',function(){navigator.clipboard.writeText(document.getElementById('li-out').value); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy';},1500);});
  })();
</script>
"""


def _heading_analyzer():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste page HTML or markdown</label>
  <textarea id="ha-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono" placeholder="<h1>Page title</h1>&#10;<h2>Section</h2>&#10;or # Page title&#10;## Section"></textarea>
  <button id="ha-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Analyze</button>
  <div id="ha-out" class="mt-4"></div>
</div>
<script>
  (function(){
    var inp=document.getElementById('ha-input'),out=document.getElementById('ha-out');
    function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
    function run(){
      var t=inp.value||''; var hs=[];
      var re=/<h([1-6])[^>]*>(.*?)<\\/h\\1>/gi; var m;
      while((m=re.exec(t))!==null) hs.push({lvl:+m[1], txt:m[2].replace(/<[^>]+>/g,'').trim()});
      if(hs.length===0){
        t.split(/\\n/).forEach(function(line){
          var mm=/^(#{1,6})\\s+(.+)$/.exec(line);
          if(mm) hs.push({lvl:mm[1].length, txt:mm[2].trim()});
        });
      }
      var counts={1:0,2:0,3:0,4:0,5:0,6:0}; hs.forEach(function(h){counts[h.lvl]++;});
      var alerts=[];
      if(counts[1]===0) alerts.push('No H1 found - every page should have exactly one H1.');
      if(counts[1]>1) alerts.push('Multiple H1s detected ('+counts[1]+'). Consolidate to a single H1.');
      var prev=0; hs.forEach(function(h){if(prev && h.lvl-prev>1) alerts.push('Skipped heading level near "'+h.txt.slice(0,40)+'..." (jumped from H'+prev+' to H'+h.lvl+').'); prev=h.lvl;});
      var html='<div class="grid md:grid-cols-3 gap-2 text-xs mb-3">';
      [1,2,3,4,5,6].forEach(function(l){html+='<div class="glass p-2"><span class="text-foreground/60">H'+l+'</span> <span class="font-display text-base ml-2">'+counts[l]+'</span></div>';});
      html+='</div>';
      if(alerts.length) html+='<ul class="text-sm text-amber-300 mb-3">'+alerts.map(function(a){return '<li>- '+esc(a)+'</li>';}).join('')+'</ul>';
      else html+='<p class="text-sm text-emerald-400 mb-3">No structural alerts.</p>';
      html+='<ul class="space-y-1 text-sm">'+hs.map(function(h){return '<li class="font-mono text-xs"><span class="text-accent">H'+h.lvl+'</span> '+'  '.repeat(h.lvl-1)+esc(h.txt)+'</li>';}).join('')+'</ul>';
      out.innerHTML=html;
    }
    document.getElementById('ha-go').addEventListener('click',run);
  })();
</script>
"""


def _headline_analyzer():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Headline</label>
  <input id="hl-input" placeholder="Type or paste your headline" class="mt-2 w-full h-12 rounded-lg bg-card/60 border border-border px-3 text-base">
  <div id="hl-out" class="mt-4 grid md:grid-cols-3 gap-3 text-sm"></div>
  <p id="hl-tips" class="mt-3 text-sm text-foreground/70"></p>
</div>
<script>
  (function(){
    var inp=document.getElementById('hl-input'),out=document.getElementById('hl-out'),tips=document.getElementById('hl-tips');
    var POWER=['free','easy','best','new','proven','instant','effective','top','ultimate','complete','essential','quick','fast','simple','powerful','expert','secret','exclusive'];
    var EMOTION=['amazing','incredible','shocking','stunning','dramatic','life-changing','game-changing','unbelievable','must-see','breakthrough'];
    function r(){
      var t=(inp.value||'').trim(); var w=t.split(/\\s+/).filter(Boolean);
      var len=t.length, words=w.length;
      var lower=t.toLowerCase();
      var pw=POWER.filter(function(p){return lower.indexOf(p)>=0;});
      var em=EMOTION.filter(function(p){return lower.indexOf(p)>=0;});
      var hasNum=/\\d/.test(t);
      var score=50;
      if(words>=6 && words<=12) score+=15;
      if(len>=40 && len<=70) score+=15;
      if(pw.length) score+=Math.min(10,pw.length*5);
      if(em.length) score+=5;
      if(hasNum) score+=5;
      if(t.endsWith('?')) score+=5;
      score=Math.min(100,score);
      out.innerHTML='<div class="glass p-3"><p class="text-xs text-foreground/60">Score</p><p class="font-display text-2xl">'+score+'/100</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Length</p><p class="font-display text-2xl">'+len+'/70</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Words</p><p class="font-display text-2xl">'+words+'</p></div>';
      var tt=[];
      if(words<6) tt.push('Add more words; 8-12 reads best.');
      if(words>14) tt.push('Trim - shorter headlines outperform.');
      if(len>70) tt.push('Title may truncate in SERPs (>70 chars).');
      if(!hasNum) tt.push('Adding a number ("7 ways", "3 mistakes") boosts CTR ~36%.');
      if(!pw.length) tt.push('Try a power word: '+POWER.slice(0,5).join(', ')+'.');
      tips.textContent=tt.length?'Tips: '+tt.join(' '):'Looks balanced.';
    }
    inp.addEventListener('input',r); r();
  })();
</script>
"""


def _readability():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste your content</label>
  <textarea id="rd-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <div id="rd-out" class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm"></div>
  <p id="rd-grade" class="mt-3 text-sm text-foreground/70"></p>
</div>
<script>
  (function(){
    var inp=document.getElementById('rd-input'),out=document.getElementById('rd-out'),grade=document.getElementById('rd-grade');
    function syll(w){w=w.toLowerCase().replace(/(?:[^laeiouy]es|[^laeiouy]e)$/,'').replace(/^y/,''); var m=w.match(/[aeiouy]{1,2}/g); return Math.max(1,m?m.length:1);}
    function r(){
      var t=(inp.value||'').trim(); if(!t){out.innerHTML='';grade.textContent='';return;}
      var sentences=(t.match(/[^.!?]+[.!?]+/g)||[t]).length;
      var words=(t.match(/\\b[\\w']+\\b/g)||[]); var nw=words.length;
      var syllables=words.reduce(function(s,w){return s+syll(w);},0);
      if(nw===0||sentences===0){out.innerHTML='';return;}
      var asl=nw/sentences, asw=syllables/nw;
      var fre=Math.round(206.835-1.015*asl-84.6*asw);
      var fkgl=Math.round((0.39*asl+11.8*asw-15.59)*10)/10;
      out.innerHTML='<div class="glass p-3"><p class="text-xs text-foreground/60">Flesch Reading Ease</p><p class="font-display text-2xl">'+fre+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Grade level</p><p class="font-display text-2xl">'+fkgl+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Sentences</p><p class="font-display text-2xl">'+sentences+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Avg sentence length</p><p class="font-display text-2xl">'+asl.toFixed(1)+'</p></div>';
      var label=fre>=90?'Very easy':fre>=80?'Easy':fre>=70?'Fairly easy':fre>=60?'Standard':fre>=50?'Fairly difficult':fre>=30?'Difficult':'Very confusing';
      grade.textContent='Reads as: '+label+'. Aim for 60-70 (standard) on marketing pages and 70-80 on blog posts.';
    }
    inp.addEventListener('input',r);
  })();
</script>
"""


def _grammar_checker():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste your text</label>
  <textarea id="gc-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <button id="gc-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Run checks</button>
  <ul id="gc-out" class="mt-4 space-y-2 text-sm"></ul>
</div>
<script>
  (function(){
    var inp=document.getElementById('gc-input'),out=document.getElementById('gc-out');
    var COMMON={'teh':'the','recieve':'receive','seperate':'separate','definately':'definitely','occured':'occurred','untill':'until','accomodate':'accommodate','its been':"it's been",'your welcome':"you're welcome",'should of':'should have','could of':'could have'};
    document.getElementById('gc-go').addEventListener('click',function(){
      var t=inp.value||''; var issues=[];
      if(/\\s{2,}/.test(t)) issues.push('Double spaces detected. Replace with single space.');
      if(/[.!?]\\s*[a-z]/.test(t)) issues.push('Sentence may not start with capital after period.');
      if(/\\s+,/.test(t)) issues.push('Comma preceded by space - move to attached form.');
      if(/\\.\\.{2,}/.test(t)) issues.push('Multiple dots used. Use single ellipsis "..." or three periods.');
      Object.keys(COMMON).forEach(function(k){
        var re=new RegExp('\\\\b'+k+'\\\\b','gi');
        if(re.test(t)) issues.push('Possible spelling issue: "'+k+'" -> consider "'+COMMON[k]+'".');
      });
      var sents=(t.match(/[^.!?]+[.!?]+/g)||[]); sents.forEach(function(s){var w=(s.match(/\\S+/g)||[]).length; if(w>30) issues.push('Long sentence ('+w+' words). Break into shorter clauses.');});
      out.innerHTML=issues.length?issues.map(function(i){return '<li class="glass p-2 border-l-2 border-amber-400">'+i+'</li>';}).join(''):'<li class="glass p-2 border-l-2 border-emerald-400">No basic issues detected. For deeper grammar checks, run through Grammarly or LanguageTool.</li>';
    });
  })();
</script>
"""


def _plagiarism_checker():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste your content</label>
  <textarea id="pc-input" rows="8" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <p class="mt-2 text-xs text-foreground/60">This tool splits the text into sentences and creates exact-match Google search links per sentence. Click each link to manually verify whether the sentence appears verbatim elsewhere on the web.</p>
  <button id="pc-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate search links</button>
  <ul id="pc-out" class="mt-4 space-y-2 text-sm"></ul>
</div>
<script>
  (function(){
    var inp=document.getElementById('pc-input'),out=document.getElementById('pc-out');
    function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
    document.getElementById('pc-go').addEventListener('click',function(){
      var t=inp.value||''; var sents=(t.match(/[^.!?]+[.!?]+/g)||[]).map(function(s){return s.trim();}).filter(function(s){return s.split(/\\s+/).length>=6;});
      out.innerHTML=sents.map(function(s,i){var u='https://www.google.com/search?q=%22'+encodeURIComponent(s.slice(0,200))+'%22'; return '<li class="glass p-3 flex items-start justify-between gap-3"><span class="flex-1">'+(i+1)+'. '+esc(s.slice(0,160))+(s.length>160?'...':'')+'</span><a href="'+u+'" target="_blank" rel="noopener" class="text-accent text-xs underline shrink-0">Search</a></li>';}).join('');
    });
  })();
</script>
"""


def _ai_content_detector():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste content to analyze</label>
  <textarea id="ai-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <button id="ai-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Analyze</button>
  <div id="ai-out" class="mt-4"></div>
  <p class="mt-3 text-xs text-foreground/60">This is a heuristic estimate based on lexical and structural patterns. It is not a definitive AI-detection tool - no detector is. Use it as a sanity check, not a verdict.</p>
</div>
<script>
  (function(){
    var inp=document.getElementById('ai-input'),out=document.getElementById('ai-out');
    var TELLS=['delve','tapestry','underscores','furthermore','moreover','nevertheless','intricate','myriad','crucially','navigate','landscape','seamlessly','realm','plethora','elevate','endeavor'];
    document.getElementById('ai-go').addEventListener('click',function(){
      var t=(inp.value||'').toLowerCase(); var words=(t.match(/[\\w']+/g)||[]); var nw=words.length;
      var sents=(t.match(/[^.!?]+[.!?]+/g)||[]); var ns=sents.length;
      if(nw<50){out.innerHTML='<p class="text-amber-400 text-sm">Need at least 50 words for meaningful analysis.</p>';return;}
      var avg=nw/Math.max(1,ns); var stdSpread=sents.map(function(s){return s.split(/\\s+/).length;}).reduce(function(s,n){return s+Math.abs(n-avg);},0)/Math.max(1,ns);
      var hits=TELLS.filter(function(w){return t.indexOf(w)>=0;});
      var score=0;
      if(avg>20) score+=20; if(stdSpread<6) score+=20; score+=Math.min(40,hits.length*8);
      if(/\\b(in conclusion|in summary|to conclude|overall)\\b/.test(t)) score+=10;
      score=Math.min(99,score);
      var verdict=score>70?'Likely AI-generated':score>40?'Possibly AI-generated':'Likely human-written';
      out.innerHTML='<div class="glass-strong p-4 rounded-lg"><p class="text-sm text-foreground/60">AI score</p><p class="font-display text-3xl">'+score+'/100</p><p class="mt-1 text-sm">'+verdict+'</p>'+(hits.length?'<p class="mt-3 text-xs text-foreground/60">Words flagged: '+hits.join(', ')+'</p>':'')+'<p class="mt-2 text-xs text-foreground/60">Avg sentence length: '+avg.toFixed(1)+' words. Variance score: '+stdSpread.toFixed(1)+'.</p></div>';
    });
  })();
</script>
"""


def _article_rewriter():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Original text</label>
  <textarea id="ar-input" rows="8" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <button id="ar-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Suggest rewrite</button>
  <textarea id="ar-out" rows="8" readonly class="mt-4 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <p class="mt-3 text-xs text-foreground/60">This swaps a curated set of common synonyms and re-orders clauses for variety. Always review the output for accuracy before publishing.</p>
</div>
<script>
  (function(){
    var SYN={'important':'critical','use':'leverage','make':'create','help':'assist','show':'demonstrate','start':'begin','end':'conclude','find':'identify','tell':'explain','also':'in addition','but':'however','because':'since','very':'highly','many':'numerous','big':'substantial','small':'modest'};
    function rewrite(t){return t.split(/(\\s+)/).map(function(w){var k=w.toLowerCase().replace(/[^a-z]/g,''); return SYN[k]?(w.charAt(0)===w.charAt(0).toUpperCase()?(SYN[k].charAt(0).toUpperCase()+SYN[k].slice(1)):SYN[k]):w;}).join('');}
    document.getElementById('ar-go').addEventListener('click',function(){document.getElementById('ar-out').value=rewrite(document.getElementById('ar-input').value||'');});
  })();
</script>
"""


def _form_field_counter():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste form HTML</label>
  <textarea id="ff-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono" placeholder="<form>...</form>"></textarea>
  <button id="ff-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Count fields</button>
  <div id="ff-out" class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm"></div>
  <p class="mt-3 text-xs text-foreground/60">Best-practice forms have 3-5 fields. Each extra field reduces conversion ~6-10%.</p>
</div>
<script>
  (function(){
    var inp=document.getElementById('ff-input'),out=document.getElementById('ff-out');
    document.getElementById('ff-go').addEventListener('click',function(){
      var t=inp.value||'';
      var inputs=(t.match(/<input\\b/gi)||[]).length;
      var textareas=(t.match(/<textarea\\b/gi)||[]).length;
      var selects=(t.match(/<select\\b/gi)||[]).length;
      var buttons=(t.match(/<button\\b/gi)||[]).length;
      var requireds=(t.match(/\\brequired\\b/gi)||[]).length;
      var total=inputs+textareas+selects;
      out.innerHTML='<div class="glass p-3"><p class="text-xs text-foreground/60">Total fields</p><p class="font-display text-2xl">'+total+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Required</p><p class="font-display text-2xl">'+requireds+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Input/textarea/select</p><p class="font-display text-2xl">'+inputs+'/'+textareas+'/'+selects+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Buttons</p><p class="font-display text-2xl">'+buttons+'</p></div>';
    });
  })();
</script>
"""


def _page_size_checker():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste page HTML or content</label>
  <textarea id="ps-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
  <div id="ps-out" class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm"></div>
</div>
<script>
  (function(){
    var inp=document.getElementById('ps-input'),out=document.getElementById('ps-out');
    function fmt(n){if(n<1024)return n+' B'; if(n<1048576)return (n/1024).toFixed(1)+' KB'; return (n/1048576).toFixed(2)+' MB';}
    function r(){
      var t=inp.value||''; var raw=new Blob([t]).size;
      var compressed=Math.round(raw*0.32);
      var imgs=(t.match(/<img\\b/gi)||[]).length;
      var scripts=(t.match(/<script\\b/gi)||[]).length;
      out.innerHTML='<div class="glass p-3"><p class="text-xs text-foreground/60">Raw HTML</p><p class="font-display text-2xl">'+fmt(raw)+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Gzipped (est)</p><p class="font-display text-2xl">'+fmt(compressed)+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Images</p><p class="font-display text-2xl">'+imgs+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Scripts</p><p class="font-display text-2xl">'+scripts+'</p></div>';
    }
    inp.addEventListener('input',r); r();
  })();
</script>
"""


def _color_contrast():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Foreground color <input type="color" id="cc-fg" value="#ffffff" class="h-11 w-full rounded-lg bg-card/60 border border-border px-2"></label>
    <label>Background color <input type="color" id="cc-bg" value="#0a1628" class="h-11 w-full rounded-lg bg-card/60 border border-border px-2"></label>
  </form>
  <div class="glass-strong p-5 rounded-lg" id="cc-prev">
    <p class="text-xs">Preview</p>
    <p id="cc-text" class="font-display text-2xl">Sample text</p>
    <p class="mt-3 text-sm" id="cc-out"></p>
  </div>
</div>
<script>
  (function(){
    var fg=document.getElementById('cc-fg'),bg=document.getElementById('cc-bg'),prev=document.getElementById('cc-prev'),txt=document.getElementById('cc-text'),out=document.getElementById('cc-out');
    function hex2rgb(h){var m=h.replace('#',''); return [parseInt(m.substr(0,2),16),parseInt(m.substr(2,2),16),parseInt(m.substr(4,2),16)];}
    function lum(rgb){return rgb.map(function(v){v/=255; return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);}).reduce(function(s,v,i){return s+v*[0.2126,0.7152,0.0722][i];},0);}
    function ratio(a,b){var L1=Math.max(lum(a),lum(b)),L2=Math.min(lum(a),lum(b)); return (L1+0.05)/(L2+0.05);}
    function r(){
      var a=hex2rgb(fg.value), b=hex2rgb(bg.value); var rt=ratio(a,b);
      prev.style.backgroundColor=bg.value; txt.style.color=fg.value;
      var aa=rt>=4.5?'PASS':'FAIL', aaa=rt>=7?'PASS':'FAIL', aalg=rt>=3?'PASS':'FAIL';
      out.innerHTML='Ratio: <span class="font-display text-xl">'+rt.toFixed(2)+':1</span><br>WCAG AA (normal): '+aa+'<br>WCAG AAA (normal): '+aaa+'<br>WCAG AA (large): '+aalg;
    }
    [fg,bg].forEach(function(e){e.addEventListener('input',r);}); r();
  })();
</script>
"""


# =============================================================================
# Keyword tools
# =============================================================================


def _keyword_suggestion():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Seed keyword</label>
    <input id="ks-seed" placeholder="e.g. seo services" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3">
    <button id="ks-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate variations</button>
    <p class="mt-3 text-xs text-foreground/60">Combines your seed with 60+ modifiers used in real search queries (intent, modifier, location, comparison, year).</p>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Suggestions</p>
    <ul id="ks-out" class="glass-strong rounded-lg p-3 max-h-96 overflow-auto space-y-1 text-sm"></ul>
    <button id="ks-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm hidden">Copy all</button>
  </div>
</div>
<script>
  (function(){
    var PRE=['best','cheap','top','professional','free','online','local','near me','affordable','fastest','reliable','expert','certified','trusted'];
    var SUF=['services','company','agency','near me','for small business','for ecommerce','for startups','prices','cost','reviews','vs','alternatives','tutorial','guide','tips','strategy','checklist','2026','case study','benefits','examples'];
    var QU=['what is','how to','why','when to','who is the best','should I'];
    function gen(s){var r=new Set(); s=s.trim().toLowerCase(); if(!s) return [];
      r.add(s);
      PRE.forEach(function(p){r.add(p+' '+s);});
      SUF.forEach(function(p){r.add(s+' '+p);});
      QU.forEach(function(p){r.add(p+' '+s);});
      ['for {audience}','in {city}','near {city}'].forEach(function(){});
      return Array.from(r);
    }
    document.getElementById('ks-go').addEventListener('click',function(){
      var s=document.getElementById('ks-seed').value; var arr=gen(s);
      var out=document.getElementById('ks-out');
      out.innerHTML=arr.map(function(k){return '<li class="flex items-center justify-between gap-2 glass p-2 rounded"><span>'+k+'</span><a target="_blank" rel="noopener" href="https://www.google.com/search?q='+encodeURIComponent(k)+'" class="text-accent text-xs underline">Search</a></li>';}).join('');
      var btn=document.getElementById('ks-copy'); btn.classList.remove('hidden');
      btn.onclick=function(){navigator.clipboard.writeText(arr.join('\\n')); btn.textContent='Copied'; setTimeout(function(){btn.textContent='Copy all';},1500);};
    });
  })();
</script>
"""


def _long_tail_kw():
    return _keyword_suggestion()


def _lsi_kw():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Primary keyword</label>
    <input id="lsi-seed" placeholder="e.g. content marketing" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3">
    <p class="mt-2 text-xs text-foreground/60">Generates LSI / semantic variants and links each to live Google + AI Overviews searches so you can verify intent overlap.</p>
    <button id="lsi-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate LSI keywords</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Semantic variations</p>
    <ul id="lsi-out" class="glass-strong rounded-lg p-3 max-h-96 overflow-auto space-y-1 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var MOD=['strategy','plan','framework','workflow','case study','examples','best practices','metrics','KPIs','tools','software','agency','services','consultant','vs marketing','for B2B','for SaaS','for ecommerce','ROI','attribution','funnel','automation','channels','playbook','template','calendar','checklist','process','definition','meaning'];
    function gen(s){if(!s) return []; var arr=new Set(); var k=s.trim().toLowerCase(); MOD.forEach(function(m){arr.add(k+' '+m); arr.add(m+' '+k);}); arr.add('what is '+k); arr.add('how does '+k+' work'); arr.add(k+' for beginners'); arr.add('advanced '+k); arr.add(k+' explained'); return Array.from(arr);}
    document.getElementById('lsi-go').addEventListener('click',function(){
      var s=document.getElementById('lsi-seed').value; var arr=gen(s);
      var out=document.getElementById('lsi-out');
      out.innerHTML=arr.map(function(k){return '<li class="flex items-center justify-between gap-2 glass p-2 rounded"><span>'+k+'</span><a target="_blank" rel="noopener" href="https://www.google.com/search?q='+encodeURIComponent(k)+'" class="text-accent text-xs underline">Verify</a></li>';}).join('');
    });
  })();
</script>
"""


def _local_keyword_gen():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Service / niche <input id="lk-svc" placeholder="dentist" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Cities (one per line) <textarea id="lk-cities" rows="6" placeholder="dallas&#10;plano&#10;frisco&#10;mckinney" class="rounded-lg bg-card/60 border border-border px-3 py-2"></textarea></label>
    <label>Variants
      <select id="lk-var" class="h-11 rounded-lg bg-card/60 border border-border px-3">
        <option value="all">All patterns</option>
        <option value="near">"near me" + "in city"</option>
        <option value="best">"best", "top", "affordable"</option>
        <option value="hours">"open now", "24 hour", "weekend"</option>
      </select>
    </label>
    <button id="lk-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Local variants</p>
    <ul id="lk-out" class="glass-strong rounded-lg p-3 max-h-96 overflow-auto space-y-1 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    function gen(svc,cities,m){var arr=new Set(); cities.forEach(function(c){c=c.trim(); if(!c) return;
      if(m==='all'||m==='near'){arr.add(svc+' near me'); arr.add(svc+' in '+c); arr.add(svc+' near '+c);}
      if(m==='all'||m==='best'){['best','top','affordable','cheap','professional'].forEach(function(p){arr.add(p+' '+svc+' in '+c);});}
      if(m==='all'||m==='hours'){['open now','24 hour','weekend','same day'].forEach(function(p){arr.add(p+' '+svc+' '+c);});}
      arr.add(c+' '+svc); arr.add(svc+' '+c+' reviews'); arr.add(svc+' '+c+' prices');
    }); return Array.from(arr);}
    document.getElementById('lk-go').addEventListener('click',function(){
      var svc=document.getElementById('lk-svc').value.trim(),cities=document.getElementById('lk-cities').value.split(/\\n/),m=document.getElementById('lk-var').value;
      if(!svc) return; var arr=gen(svc,cities,m);
      document.getElementById('lk-out').innerHTML=arr.map(function(k){return '<li class="flex items-center justify-between gap-2 glass p-2 rounded"><span>'+k+'</span><a target="_blank" rel="noopener" href="https://www.google.com/search?q='+encodeURIComponent(k)+'" class="text-accent text-xs underline">Search</a></li>';}).join('');
    });
  })();
</script>
"""


def _negative_kw():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Your keywords / search terms (one per line)</label>
    <textarea id="nk-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm"></textarea>
    <button id="nk-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Suggest negatives</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Suggested negative keywords</p>
    <pre id="nk-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
  </div>
</div>
<script>
  (function(){
    var COMMON=['free','jobs','salary','careers','review','reviews','complaint','complaints','vs','difference','diy','tutorial','meaning','definition','wikipedia','reddit','forum','torrent','crack','download','course','udemy','lesson','example','sample'];
    document.getElementById('nk-go').addEventListener('click',function(){
      var lines=(document.getElementById('nk-input').value||'').split(/\\n/).map(function(s){return s.trim().toLowerCase();}).filter(Boolean);
      var found=new Set(); lines.forEach(function(l){COMMON.forEach(function(n){if(l.indexOf(n)>=0) found.add(n);});});
      document.getElementById('nk-out').textContent=Array.from(found).map(function(w){return '-'+w;}).join('\\n')||'No common negatives detected.';
    });
  })();
</script>
"""


def _gbp_keyword():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Business name <input id="gbp-name" placeholder="Acme Dental" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>City <input id="gbp-city" placeholder="dallas tx" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Keywords (one per line) <textarea id="gbp-kws" rows="6" placeholder="emergency dentist&#10;teeth whitening&#10;family dentist" class="rounded-lg bg-card/60 border border-border px-3 py-2"></textarea></label>
    <button id="gbp-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate Map Pack searches</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Search links</p>
    <ul id="gbp-out" class="glass-strong rounded-lg p-3 max-h-96 overflow-auto space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    document.getElementById('gbp-go').addEventListener('click',function(){
      var name=document.getElementById('gbp-name').value.trim(),city=document.getElementById('gbp-city').value.trim();
      var kws=document.getElementById('gbp-kws').value.split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      if(!city||!kws.length) return;
      document.getElementById('gbp-out').innerHTML=kws.map(function(k){var q=k+' '+city; var u='https://www.google.com/maps/search/'+encodeURIComponent(q); return '<li class="flex items-center justify-between gap-2 glass p-2 rounded"><span>'+k+(name?' / brand: '+name:'')+'</span><a target="_blank" rel="noopener" href="'+u+'" class="text-accent text-xs underline">Open Map Pack</a></li>';}).join('');
    });
  })();
</script>
"""


def _geo_modifier():
    return _local_keyword_gen()


def _keyword_difficulty():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Keyword <input id="kd-kw" placeholder="seo services" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Estimated monthly volume <input type="number" id="kd-vol" value="5000" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Top result domain rating (1-100) <input type="number" id="kd-dr" value="65" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Number of paid ads showing <input type="number" id="kd-ads" value="2" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
  </form>
  <div class="glass-strong p-5 rounded-lg">
    <p class="text-xs text-foreground/60">Difficulty score</p>
    <p id="kd-out" class="font-display text-3xl">-</p>
    <p id="kd-out2" class="mt-2 text-sm text-foreground/70"></p>
  </div>
</div>
<script>
  (function(){
    function r(){
      var kw=document.getElementById('kd-kw').value.trim();
      var vol=parseFloat(document.getElementById('kd-vol').value)||0;
      var dr=parseFloat(document.getElementById('kd-dr').value)||0;
      var ads=parseFloat(document.getElementById('kd-ads').value)||0;
      var len=kw.split(/\\s+/).filter(Boolean).length;
      var score=Math.min(100,Math.round(dr*0.6+ads*5+(vol>10000?15:vol>1000?8:3)-(len-1)*5));
      var label=score<30?'Easy':score<50?'Moderate':score<70?'Hard':'Very hard';
      document.getElementById('kd-out').textContent=score+'/100';
      document.getElementById('kd-out2').textContent=label+'. '+(score>60?'Target long-tail variants first; build authority before attempting.':score>40?'Reachable with strong content + 5-10 quality links.':'Achievable with solid on-page SEO.');
    }
    ['kd-kw','kd-vol','kd-dr','kd-ads'].forEach(function(id){document.getElementById(id).addEventListener('input',r);}); r();
  })();
</script>
"""


def _kw_cluster_grouper():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Keywords (one per line)</label>
    <textarea id="kc-input" rows="14" placeholder="seo services&#10;seo agency&#10;seo company&#10;link building&#10;backlink building&#10;backlink services" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm"></textarea>
    <button id="kc-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Cluster keywords</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Groups</p>
    <div id="kc-out" class="glass-strong rounded-lg p-3 max-h-96 overflow-auto text-sm space-y-3"></div>
    <p class="mt-3 text-xs text-foreground/60">Groups by shared core token (after stop-word removal). Use as the basis for content-cluster mapping.</p>
  </div>
</div>
<script>
  (function(){
    var STOP=new Set(['the','a','an','of','to','and','in','for','on','is','at','it','as','with','by','that','this','from','or','near','your','my','our']);
    function tokens(k){return k.toLowerCase().split(/\\s+/).filter(function(w){return w && !STOP.has(w);});}
    document.getElementById('kc-go').addEventListener('click',function(){
      var lines=(document.getElementById('kc-input').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      var groups={};
      lines.forEach(function(k){var ts=tokens(k); var key=ts.sort().join(' ').replace(/\\s+/g,'').slice(0,80); var coreKey=ts[0]||k.toLowerCase().slice(0,12);
        if(!groups[coreKey]) groups[coreKey]={core:coreKey, items:[]};
        groups[coreKey].items.push(k);
      });
      // Merge groups that share token
      var arr=Object.values(groups).sort(function(a,b){return b.items.length-a.items.length;});
      document.getElementById('kc-out').innerHTML=arr.map(function(g){return '<div class="glass p-3"><p class="text-xs text-accent">cluster: '+g.core+' ('+g.items.length+')</p><ul class="mt-2 space-y-1">'+g.items.map(function(k){return '<li class="text-xs">- '+k+'</li>';}).join('')+'</ul></div>';}).join('');
    });
  })();
</script>
"""


def _competitor_kw_gap():
    return """
<div class="glass p-6 grid md:grid-cols-3 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Your keywords</label>
    <textarea id="cg-mine" rows="14" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm"></textarea>
  </div>
  <div>
    <label class="text-sm font-display font-semibold">Competitor keywords</label>
    <textarea id="cg-comp" rows="14" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm"></textarea>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Gap (theirs minus yours)</p>
    <ul id="cg-out" class="glass-strong rounded-lg p-3 max-h-96 overflow-auto space-y-1 text-sm"></ul>
    <button id="cg-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Find gap</button>
  </div>
</div>
<script>
  (function(){
    document.getElementById('cg-go').addEventListener('click',function(){
      var mine=new Set((document.getElementById('cg-mine').value||'').split(/\\n/).map(function(s){return s.trim().toLowerCase();}).filter(Boolean));
      var comp=(document.getElementById('cg-comp').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      var gap=comp.filter(function(k){return !mine.has(k.toLowerCase());});
      document.getElementById('cg-out').innerHTML=gap.length?gap.map(function(k){return '<li class="glass p-2 rounded"><span>'+k+'</span> <a target="_blank" rel="noopener" href="https://www.google.com/search?q='+encodeURIComponent(k)+'" class="text-accent text-xs underline ml-2">Search</a></li>';}).join(''):'<li class="text-foreground/60">No gap detected.</li>';
    });
  })();
</script>
"""


def _content_gap_analyzer():
    return _competitor_kw_gap()


def _search_intent():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Keywords (one per line)</label>
  <textarea id="si-input" rows="8" placeholder="best seo agency&#10;what is seo&#10;buy seo services&#10;seo agency reviews" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm"></textarea>
  <button id="si-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Classify</button>
  <ul id="si-out" class="mt-4 space-y-2 text-sm"></ul>
</div>
<script>
  (function(){
    function classify(k){var s=k.toLowerCase();
      if(/\\b(buy|hire|order|book|price|cost|cheapest|near me|for sale|coupon|discount)\\b/.test(s)) return {label:'Transactional', color:'emerald'};
      if(/\\b(best|top|review|vs|compare|alternative)\\b/.test(s)) return {label:'Commercial', color:'amber'};
      if(/\\b(login|sign in|account|dashboard|app|download)\\b/.test(s)) return {label:'Navigational', color:'sky'};
      if(/\\b(what|how|why|when|where|who|guide|tutorial|examples|definition|meaning)\\b/.test(s)) return {label:'Informational', color:'fuchsia'};
      return {label:'Informational', color:'fuchsia'};
    }
    document.getElementById('si-go').addEventListener('click',function(){
      var lines=(document.getElementById('si-input').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      document.getElementById('si-out').innerHTML=lines.map(function(k){var c=classify(k); return '<li class="glass p-3 flex items-center justify-between gap-3"><span>'+k+'</span><span class="px-2 py-1 rounded text-xs bg-'+c.color+'-500/20 text-'+c.color+'-300">'+c.label+'</span></li>';}).join('');
    });
  })();
</script>
"""


def _paa_extractor():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Topic / keyword</label>
    <input id="paa-input" placeholder="seo services" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3">
    <button id="paa-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate questions</button>
    <p class="mt-3 text-xs text-foreground/60">Combines your topic with the most common People Also Ask question stems and generates a Google search link per question - click any link to see real PAA results to mine.</p>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Questions</p>
    <ul id="paa-out" class="glass-strong rounded-lg p-3 max-h-96 overflow-auto space-y-1 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var STEMS=['what is','how does','how to do','why is','why do','when should','where to find','who needs','what are the benefits of','what are the costs of','how much does','is it worth','can you do','should I','how long does','how often','what is the best','what is included in','what is the difference between','how do I choose','how do I get started with'];
    document.getElementById('paa-go').addEventListener('click',function(){
      var k=document.getElementById('paa-input').value.trim(); if(!k) return;
      var out=document.getElementById('paa-out');
      out.innerHTML=STEMS.map(function(s){var q=s+' '+k+'?'; var u='https://www.google.com/search?q='+encodeURIComponent(q); return '<li class="flex items-center justify-between gap-2 glass p-2 rounded"><span>'+q+'</span><a target="_blank" rel="noopener" href="'+u+'" class="text-accent text-xs underline">PAA</a></li>';}).join('');
    });
  })();
</script>
"""


def _question_generator():
    return _paa_extractor()


# =============================================================================
# Meta / title / description tools
# =============================================================================


def _meta_desc_checker():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Meta description</label>
  <textarea id="md-input" rows="4" maxlength="240" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <div id="md-out" class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm"></div>
  <p id="md-tip" class="mt-3 text-sm text-foreground/70"></p>
</div>
<script>
  (function(){
    var inp=document.getElementById('md-input'),out=document.getElementById('md-out'),tip=document.getElementById('md-tip');
    function r(){
      var t=inp.value||''; var l=t.length, w=(t.trim().match(/\\S+/g)||[]).length;
      var px=Math.round(t.length*7.5); // ~7.5px per char average for Arial 13px
      out.innerHTML='<div class="glass p-3"><p class="text-xs text-foreground/60">Characters</p><p class="font-display text-2xl">'+l+'/160</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Words</p><p class="font-display text-2xl">'+w+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Pixel width (est)</p><p class="font-display text-2xl">'+px+'</p></div>'+
        '<div class="glass p-3"><p class="text-xs text-foreground/60">Status</p><p class="font-display text-2xl">'+(l<=160&&l>=120?'OK':l>160?'Too long':'Short')+'</p></div>';
      var t2=l>160?'Truncates in SERPs after ~160 chars / 920 px.':l<120?'Too short - leaves CTA opportunities on the table.':'Length is in the recommended sweet spot.';
      tip.textContent=t2;
    }
    inp.addEventListener('input',r); r();
  })();
</script>
"""


def _meta_desc_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Page topic / primary keyword <input id="mg-kw" placeholder="seo services for dentists" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Brand <input id="mg-brand" placeholder="Shahab Abbasi" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Unique angle <input id="mg-angle" placeholder="90-day ROI guarantee" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Audience / location <input id="mg-aud" placeholder="for North American clinics" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="mg-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate variations</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Variations</p>
    <ul id="mg-out" class="space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var T=[
      "{kw} from {brand}: {angle}, {aud}.",
      "Get {kw} that delivers measurable results. {brand} - {angle}.",
      "{brand} runs senior-led {kw} programs {aud}. {angle}.",
      "Drive growth with {kw} {aud}. Built around {angle} - {brand}.",
      "Free audit of your current {kw}. {brand} backs every plan with {angle}.",
      "Evidence-based {kw} from {brand}. {angle} on every engagement, {aud}."
    ];
    document.getElementById('mg-go').addEventListener('click',function(){
      var ctx={kw:document.getElementById('mg-kw').value||'SEO',brand:document.getElementById('mg-brand').value||'our team',angle:document.getElementById('mg-angle').value||'transparent reporting',aud:document.getElementById('mg-aud').value||'for ambitious operators'};
      var out=document.getElementById('mg-out');
      out.innerHTML=T.map(function(t){var s=t.replace(/\\{(\\w+)\\}/g,function(_,k){return ctx[k]||'';}).slice(0,160); return '<li class="glass p-3 flex items-start justify-between gap-3"><span>'+s+'</span><button class="text-accent text-xs underline" onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent);this.textContent=&quot;Copied&quot;">Copy</button></li>';}).join('');
    });
  })();
</script>
"""


def _ai_meta_desc():
    return _meta_desc_generator()


def _ai_title():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Primary keyword <input id="at-kw" placeholder="content marketing services" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Brand or year <input id="at-brand" placeholder="Shahab Abbasi 2026" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="at-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate titles</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Title variations (60-char optimised)</p>
    <ul id="at-out" class="space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var T=[
      '{kw} - Built for Growth | {brand}',
      '7 {kw} Mistakes Killing Your Pipeline (Fix Today)',
      '{kw} That Pays Back in 90 Days - {brand}',
      'How To Pick a {kw} Partner: 2026 Buyer Guide',
      'The Complete {kw} Playbook ({brand})',
      '{kw}: Pricing, ROI, Timelines | {brand}'
    ];
    document.getElementById('at-go').addEventListener('click',function(){
      var ctx={kw:document.getElementById('at-kw').value||'SEO',brand:document.getElementById('at-brand').value||'2026'};
      document.getElementById('at-out').innerHTML=T.map(function(t){var s=t.replace(/\\{(\\w+)\\}/g,function(_,k){return ctx[k]||'';}).slice(0,60); return '<li class="glass p-3 flex items-start justify-between gap-3"><span>'+s+'</span><span class="text-xs text-foreground/60">'+s.length+'/60</span></li>';}).join('');
    });
  })();
</script>
"""


def _title_optimizer():
    return _headline_analyzer()


def _bulk_title_checker():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Titles (one per line)</label>
  <textarea id="bt-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <button id="bt-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Analyze</button>
  <table class="mt-4 w-full text-sm">
    <thead><tr class="text-left text-foreground/60"><th>Title</th><th>Length</th><th>Status</th></tr></thead>
    <tbody id="bt-out"></tbody>
  </table>
</div>
<script>
  (function(){
    document.getElementById('bt-go').addEventListener('click',function(){
      var lines=(document.getElementById('bt-input').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      document.getElementById('bt-out').innerHTML=lines.map(function(t){var l=t.length; var s=l<30?'Short':l>60?'Too long':'OK'; return '<tr class="border-t border-border/30"><td class="py-1">'+t+'</td><td>'+l+'</td><td class="'+(s==='OK'?'text-emerald-400':s==='Too long'?'text-red-400':'text-amber-400')+'">'+s+'</td></tr>';}).join('');
    });
  })();
</script>
"""


def _ai_faq_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Topic</label>
    <input id="faq-topic" placeholder="seo for dentists" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3">
    <button id="faq-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate FAQs + JSON-LD</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">JSON-LD output</p>
    <pre id="faq-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
  </div>
</div>
<script>
  (function(){
    var STEMS=[['How long does {t} take to show results?','Most engagements show meaningful movement in 60-90 days.'],['How much does {t} cost in 2026?','Programs start at $1,750 monthly and scale to $12,500+ for enterprise.'],['Do you guarantee results for {t}?','Yes. We offer a 90-day ROI guarantee tied to a measurable milestone.'],['How is {t} different from generic SEO?','It is purpose-built around the buyer behavior, schema, and platform constraints of your niche.'],['Do you work with in-house teams?','Yes - fully managed or fractional consulting depending on stage.'],['How do you track AI search visibility?','We monitor citations across ChatGPT, Perplexity, Claude, Gemini, and Google AI Overviews weekly.'],['What reporting can I expect?','Live dashboards plus a monthly executive readout covering rankings, traffic, AI citations, and pipeline.'],['Can you support international rollouts?','Yes - hreflang, multilingual content, ccTLD strategy, and localized link building across 22+ languages.']];
    document.getElementById('faq-go').addEventListener('click',function(){
      var t=document.getElementById('faq-topic').value.trim()||'this service';
      var arr=STEMS.map(function(p){return {'@type':'Question','name':p[0].replace(/\\{t\\}/g,t),'acceptedAnswer':{'@type':'Answer','text':p[1]}};});
      var out={'@context':'https://schema.org','@type':'FAQPage','mainEntity':arr};
      document.getElementById('faq-out').textContent='<script type="application/ld+json">\\n'+JSON.stringify(out,null,2)+'\\n<\\/script>';
    });
  })();
</script>
"""


# =============================================================================
# URL / Link / HTTP tools
# =============================================================================


def _open_in_tab_tool(label, query_builder_js, instruction):
    """Generic tool: paste URL list -> generate links that open in new tabs."""
    return f"""
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">{label} (one URL or item per line)</label>
  <textarea id="ot-input" rows="8" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
  <p class="mt-2 text-xs text-foreground/60">{instruction}</p>
  <button id="ot-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate links</button>
  <button id="ot-open" class="mt-3 ml-2 rounded-xl border border-border/60 px-4 py-2 text-sm hidden">Open all in tabs</button>
  <ul id="ot-out" class="mt-4 glass-strong rounded-lg p-3 max-h-96 overflow-auto space-y-2 text-sm"></ul>
</div>
<script>
  (function(){{
    var inp=document.getElementById('ot-input'),out=document.getElementById('ot-out'),openAll=document.getElementById('ot-open');
    function esc(s){{return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}}
    document.getElementById('ot-go').addEventListener('click',function(){{
      var lines=(inp.value||'').split(/\\r?\\n/).map(function(s){{return s.trim();}}).filter(Boolean);
      var urls=lines.map(function(raw){{ {query_builder_js} return u; }});
      out.innerHTML=lines.map(function(raw,i){{var u=urls[i]; return '<li class="glass p-2 rounded flex items-center justify-between gap-2"><span class="text-xs font-mono">'+esc(raw)+'</span><a target="_blank" rel="noopener" href="'+u+'" class="text-accent text-xs underline shrink-0">Open</a></li>';}}).join('');
      openAll.classList.remove('hidden');
      openAll.onclick=function(){{ urls.forEach(function(u){{ window.open(u,'_blank','noopener'); }}); }};
    }});
  }})();
</script>
"""


def _google_index_checker():
    return _open_in_tab_tool(
        "URLs to check in Google index",
        "var clean=raw.replace(/^https?:\\/\\//,'').replace(/\\/$/,''); var u='https://www.google.com/search?q=site%3A'+encodeURIComponent(clean);",
        "Each URL becomes a site:URL Google search. Click any link to manually verify whether the page is indexed.",
    )


def _index_coverage_checker():
    return _google_index_checker()


def _bulk_indexing_checker():
    return _bulk_index_checker()


def _force_google_indexing():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">URL to push for indexing</label>
  <input id="fi-input" placeholder="https://example.com/new-page" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <div class="mt-3 flex flex-wrap gap-2">
    <button id="fi-gsc" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Open in Google Search Console</button>
    <button id="fi-bing" class="rounded-xl border border-border/60 px-4 py-2 text-sm">Open in Bing Webmaster</button>
    <button id="fi-indexnow" class="rounded-xl border border-border/60 px-4 py-2 text-sm">Generate IndexNow payload</button>
    <button id="fi-ping" class="rounded-xl border border-border/60 px-4 py-2 text-sm">Open Google ping URL</button>
  </div>
  <pre id="fi-out" class="mt-4 text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg"></pre>
  <p class="mt-3 text-xs text-foreground/60">Fastest indexing path: GSC URL Inspection -> Request Indexing (works for verified domains). For new sites, also submit your sitemap to GSC + Bing and run an IndexNow POST.</p>
</div>
<script>
  (function(){
    var inp=document.getElementById('fi-input');
    document.getElementById('fi-gsc').addEventListener('click',function(){var u=inp.value.trim(); if(!u) return; window.open('https://search.google.com/search-console/inspect?resource_id='+encodeURIComponent(u.replace(/\\/[^/]*$/,'/'))+'&id='+encodeURIComponent(u),'_blank','noopener');});
    document.getElementById('fi-bing').addEventListener('click',function(){window.open('https://www.bing.com/webmasters/home','_blank','noopener');});
    document.getElementById('fi-ping').addEventListener('click',function(){var u=inp.value.trim(); if(!u) return; window.open('https://www.google.com/search?q=site%3A'+encodeURIComponent(u),'_blank','noopener');});
    document.getElementById('fi-indexnow').addEventListener('click',function(){var u=inp.value.trim(); if(!u) return; var host; try{host=new URL(u).hostname;}catch(e){host='example.com';} var payload={host:host,key:'YOUR_INDEXNOW_KEY',keyLocation:'https://'+host+'/YOUR_INDEXNOW_KEY.txt',urlList:[u]}; document.getElementById('fi-out').textContent='POST https://api.indexnow.org/indexnow\\nContent-Type: application/json\\n\\n'+JSON.stringify(payload,null,2);});
  })();
</script>
"""


def _serp_checker():
    return _open_in_tab_tool(
        "Keywords to check in SERP",
        "var u='https://www.google.com/search?q='+encodeURIComponent(raw);",
        "Each keyword opens in a fresh Google search so you can see live rankings.",
    )


def _ai_overview_visibility():
    return _open_in_tab_tool(
        "Queries to test for Google AI Overviews",
        "var u='https://www.google.com/search?q='+encodeURIComponent(raw)+'&udm=14';",
        "Opens each query in Google with AI Overviews enabled (udm=14). Capture the AI Overview citations to see which sources Google trusts for the topic.",
    )


def _ai_search_prompt_tester():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Prompt to test across AI engines</label>
  <textarea id="ai-prompt" rows="4" placeholder="What is the best SEO agency for SaaS in 2026?" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <div class="mt-3 grid sm:grid-cols-2 lg:grid-cols-4 gap-2 text-sm">
    <a id="ai-gpt" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">ChatGPT</a>
    <a id="ai-pp" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Perplexity</a>
    <a id="ai-cl" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Claude</a>
    <a id="ai-gm" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Gemini</a>
    <a id="ai-go" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Google AI Overview</a>
    <a id="ai-bg" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Bing Copilot</a>
    <a id="ai-yo" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">You.com</a>
    <a id="ai-px" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Phind</a>
  </div>
  <p class="mt-3 text-xs text-foreground/60">Each link opens that AI engine pre-loaded with your prompt (where the engine supports query parameters). Compare which sources each cites.</p>
</div>
<script>
  (function(){
    var inp=document.getElementById('ai-prompt');
    function r(){
      var q=encodeURIComponent(inp.value||'');
      document.getElementById('ai-gpt').href='https://chat.openai.com/?q='+q;
      document.getElementById('ai-pp').href='https://www.perplexity.ai/?q='+q;
      document.getElementById('ai-cl').href='https://claude.ai/new?q='+q;
      document.getElementById('ai-gm').href='https://gemini.google.com/?q='+q;
      document.getElementById('ai-go').href='https://www.google.com/search?udm=14&q='+q;
      document.getElementById('ai-bg').href='https://www.bing.com/search?q='+q+'&showconv=1';
      document.getElementById('ai-yo').href='https://you.com/search?q='+q;
      document.getElementById('ai-px').href='https://www.phind.com/search?q='+q;
    }
    inp.addEventListener('input',r); r();
  })();
</script>
"""


def _chatgpt_citation():
    return _ai_search_prompt_tester()


def _perplexity_citation():
    return _ai_search_prompt_tester()


def _ai_content_optimizer():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste content to optimise for AI Overviews / LLM answers</label>
  <textarea id="ao-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <button id="ao-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Score AI-readiness</button>
  <div id="ao-out" class="mt-4"></div>
</div>
<script>
  (function(){
    document.getElementById('ao-go').addEventListener('click',function(){
      var t=document.getElementById('ao-input').value||''; var checks=[];
      var has_q=/\\b(what|how|why|when|where|who) /i.test(t);
      var has_first_sentence_definition=/^[A-Z][^.!?]{20,200}\\bis\\b/m.test(t.split(/\\n\\n/)[0]||'');
      var lists=(t.match(/^(\\s*[-*]|\\s*\\d+\\.)\\s+/gm)||[]).length;
      var headings=(t.match(/^#{1,3}\\s+|<h[1-6]/gim)||[]).length;
      var citations=(t.match(/https?:\\/\\//g)||[]).length;
      checks.push({label:'Question stems present',ok:has_q});
      checks.push({label:'Lead sentence defines the entity',ok:has_first_sentence_definition});
      checks.push({label:'Lists / steps included',ok:lists>=3});
      checks.push({label:'Headings present',ok:headings>=2});
      checks.push({label:'Outbound citations',ok:citations>=2});
      var score=Math.round((checks.filter(function(c){return c.ok;}).length/checks.length)*100);
      document.getElementById('ao-out').innerHTML='<div class="glass-strong p-4 rounded-lg"><p class="text-xs text-foreground/60">AI-readiness score</p><p class="font-display text-3xl">'+score+'/100</p><ul class="mt-3 text-sm space-y-1">'+checks.map(function(c){return '<li class="'+(c.ok?'text-emerald-400':'text-amber-400')+'">'+(c.ok?'PASS':'TODO')+' - '+c.label+'</li>';}).join('')+'</ul></div>';
    });
  })();
</script>
"""


def _canonical_checker():
    return _open_in_tab_tool(
        "URLs to check canonical for",
        "var u='view-source:'+raw;",
        "Opens view-source for each URL. Search the source for `rel=\"canonical\"` to verify the canonical link tag.",
    )


def _canonical_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Canonical URL <input id="ca-url" placeholder="https://example.com/page" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Hreflang locales (one per line, optional) <textarea id="ca-hf" rows="3" placeholder="en https://example.com/page&#10;es https://example.com/es/page" class="rounded-lg bg-card/60 border border-border px-3 py-2"></textarea></label>
  </form>
  <div>
    <p class="font-display font-semibold mb-2 text-sm">Generated tags</p>
    <pre id="ca-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg"></pre>
    <button id="ca-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy</button>
  </div>
</div>
<script>
  (function(){
    function r(){
      var u=document.getElementById('ca-url').value.trim();
      var hf=(document.getElementById('ca-hf').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      var s=u?'<link rel="canonical" href="'+u+'">\\n':'';
      hf.forEach(function(line){var m=line.split(/\\s+/); if(m.length>=2) s+='<link rel="alternate" hreflang="'+m[0]+'" href="'+m.slice(1).join(' ')+'">\\n';});
      if(hf.length) s+='<link rel="alternate" hreflang="x-default" href="'+u+'">';
      document.getElementById('ca-out').textContent=s;
    }
    ['ca-url','ca-hf'].forEach(function(id){document.getElementById(id).addEventListener('input',r);}); r();
    document.getElementById('ca-copy').addEventListener('click',function(){navigator.clipboard.writeText(document.getElementById('ca-out').textContent); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy';},1500);});
  })();
</script>
"""


def _hreflang_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Locale URLs (one per line, "lang URL")</label>
    <textarea id="hl-input" rows="10" placeholder="en https://example.com/&#10;en-US https://example.com/&#10;es https://example.com/es/&#10;fr https://example.com/fr/" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
    <button id="hl-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate</button>
  </div>
  <div>
    <p class="font-display font-semibold mb-2 text-sm">hreflang tags</p>
    <pre id="hl-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
  </div>
</div>
<script>
  (function(){
    document.getElementById('hl-go').addEventListener('click',function(){
      var lines=(document.getElementById('hl-input').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      var s=lines.map(function(l){var m=l.split(/\\s+/); return m.length>=2?'<link rel="alternate" hreflang="'+m[0]+'" href="'+m.slice(1).join(' ')+'">':'';}).filter(Boolean).join('\\n');
      var first=lines[0]?lines[0].split(/\\s+/).slice(1).join(' '):'';
      if(first) s+='\\n<link rel="alternate" hreflang="x-default" href="'+first+'">';
      document.getElementById('hl-out').textContent=s;
    });
  })();
</script>
"""


def _broken_link_checker():
    return _open_in_tab_tool(
        "URLs to check for HTTP status",
        "var u=raw;",
        "Opens each URL in a new tab. Browser displays 404/500 pages directly. For an automated CSV, install Screaming Frog SEO Spider (free up to 500 URLs).",
    )


def _redirect_chain_checker():
    return _broken_link_checker()


def _http_status_checker():
    return _broken_link_checker()


def _http_header_inspector():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">URL</label>
  <input id="hh-url" placeholder="https://example.com" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <div class="mt-3 flex flex-wrap gap-2">
    <button id="hh-go" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Fetch headers</button>
    <a id="hh-curl" class="rounded-xl border border-border/60 px-4 py-2 text-sm hover:bg-white/5">Open Wormly Header Check</a>
    <a id="hh-redbot" class="rounded-xl border border-border/60 px-4 py-2 text-sm hover:bg-white/5">Open Redbot.org</a>
  </div>
  <pre id="hh-out" class="mt-4 text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg"></pre>
  <p class="mt-3 text-xs text-foreground/60">Many sites block cross-origin fetches. If the in-browser fetch fails, use the external tools - they bypass CORS by fetching server-side.</p>
</div>
<script>
  (function(){
    var inp=document.getElementById('hh-url'),out=document.getElementById('hh-out');
    function up(){var u=encodeURIComponent(inp.value||''); document.getElementById('hh-curl').href='https://www.wormly.com/test_http_header?url='+u; document.getElementById('hh-redbot').href='https://redbot.org/?uri='+u;}
    inp.addEventListener('input',up); up();
    document.getElementById('hh-go').addEventListener('click',function(){
      var u=inp.value.trim(); if(!u){return;}
      out.textContent='Fetching ...';
      fetch(u,{method:'HEAD',mode:'cors'}).then(function(r){var h=[]; r.headers.forEach(function(v,k){h.push(k+': '+v);}); out.textContent='Status: '+r.status+'\\n'+h.join('\\n');}).catch(function(e){out.textContent='Direct fetch blocked by CORS. Use the external tools above for full headers.\\n\\n'+e.message;});
    });
  })();
</script>
"""


def _anchor_text_analyzer():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste page HTML</label>
  <textarea id="an-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
  <button id="an-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Extract anchor text</button>
  <div id="an-out" class="mt-4"></div>
</div>
<script>
  (function(){
    document.getElementById('an-go').addEventListener('click',function(){
      var t=document.getElementById('an-input').value||''; var arr=[];
      var re=/<a\\b[^>]*href=("|')([^"']+)\\1[^>]*>([\\s\\S]*?)<\\/a>/gi; var m;
      while((m=re.exec(t))!==null){var txt=m[3].replace(/<[^>]+>/g,'').trim(); arr.push({href:m[2],text:txt||'(empty)'});}
      var counts={}; arr.forEach(function(a){counts[a.text]=(counts[a.text]||0)+1;});
      var sorted=Object.entries(counts).sort(function(a,b){return b[1]-a[1];});
      var html='<p class="text-sm">Total anchors: <span class="font-display text-xl">'+arr.length+'</span></p>';
      html+='<table class="mt-3 w-full text-sm"><thead><tr class="text-left text-foreground/60"><th>Anchor text</th><th>Count</th><th>%</th></tr></thead><tbody>';
      sorted.forEach(function(s){html+='<tr class="border-t border-border/30"><td class="py-1">'+s[0]+'</td><td>'+s[1]+'</td><td>'+(arr.length?(s[1]/arr.length*100).toFixed(1):0)+'%</td></tr>';});
      html+='</tbody></table>';
      document.getElementById('an-out').innerHTML=html;
    });
  })();
</script>
"""


def _anchor_text_distribution():
    return _anchor_text_analyzer()


def _xml_to_url():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Paste XML sitemap content</label>
  <textarea id="xu-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono" placeholder="<urlset>...</urlset>"></textarea>
  <button id="xu-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Extract URLs</button>
  <textarea id="xu-out" rows="10" readonly class="mt-4 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
  <p id="xu-count" class="mt-2 text-xs text-foreground/60">0 URLs extracted</p>
</div>
<script>
  (function(){
    document.getElementById('xu-go').addEventListener('click',function(){
      var t=document.getElementById('xu-input').value||''; var urls=[];
      var re=/<loc[^>]*>([^<]+)<\\/loc>/gi; var m;
      while((m=re.exec(t))!==null) urls.push(m[1].trim());
      document.getElementById('xu-out').value=urls.join('\\n');
      document.getElementById('xu-count').textContent=urls.length+' URLs extracted';
    });
  })();
</script>
"""


def _bulk_url_issue():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">URLs to audit (one per line)</label>
  <textarea id="bu-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
  <button id="bu-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Audit URLs</button>
  <table class="mt-4 w-full text-sm">
    <thead><tr class="text-left text-foreground/60"><th>URL</th><th>Length</th><th>Depth</th><th>Issues</th></tr></thead>
    <tbody id="bu-out"></tbody>
  </table>
</div>
<script>
  (function(){
    document.getElementById('bu-go').addEventListener('click',function(){
      var lines=(document.getElementById('bu-input').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      document.getElementById('bu-out').innerHTML=lines.map(function(u){
        var issues=[]; if(u.length>100) issues.push('long'); if(/[A-Z]/.test(u)) issues.push('uppercase'); if(/_/.test(u)) issues.push('underscore'); if(/(?:%20|\\s)/.test(u)) issues.push('space'); if(/[?&]\\w+=\\w+&/.test(u)) issues.push('multi-param'); if(/\\.html$/.test(u)) issues.push('.html ext');
        var path=''; try{path=new URL(u.indexOf('://')>=0?u:'https://'+u).pathname;}catch(e){path=u;}
        var depth=path.split('/').filter(Boolean).length;
        return '<tr class="border-t border-border/30"><td class="py-1 font-mono text-xs">'+u+'</td><td>'+u.length+'</td><td>'+depth+'</td><td class="'+(issues.length?'text-amber-300':'text-emerald-300')+'">'+(issues.length?issues.join(', '):'OK')+'</td></tr>';
      }).join('');
    });
  })();
</script>
"""


def _backlink_quality():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Referring domains (one per line)</label>
  <textarea id="bk-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
  <button id="bk-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Score backlink profile</button>
  <table class="mt-4 w-full text-sm">
    <thead><tr class="text-left text-foreground/60"><th>Domain</th><th>Heuristic risk</th></tr></thead>
    <tbody id="bk-out"></tbody>
  </table>
  <p class="mt-3 text-xs text-foreground/60">Heuristic flags very generic / low-quality patterns. For real DR/Spam Score signals run through Ahrefs, Moz, or SEMrush.</p>
</div>
<script>
  (function(){
    var BAD=['.tk','.ml','.ga','.cf','.gq','blogspot','wordpress.com','medium.com','tumblr.com','livejournal','weebly','sites.google'];
    document.getElementById('bk-go').addEventListener('click',function(){
      var lines=(document.getElementById('bk-input').value||'').split(/\\n/).map(function(s){return s.trim().toLowerCase();}).filter(Boolean);
      document.getElementById('bk-out').innerHTML=lines.map(function(d){
        var hit=BAD.filter(function(b){return d.indexOf(b)>=0;});
        var risk=hit.length?'<span class="text-amber-300">flagged: '+hit.join(', ')+'</span>':'<span class="text-emerald-300">looks clean</span>';
        return '<tr class="border-t border-border/30"><td class="py-1 font-mono text-xs">'+d+'</td><td>'+risk+'</td></tr>';
      }).join('');
    });
  })();
</script>
"""


def _url_inspector():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">URL to inspect</label>
  <input id="ui-url" placeholder="https://example.com/path?query=value#hash" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <div id="ui-out" class="mt-4 grid sm:grid-cols-2 gap-3 text-sm"></div>
</div>
<script>
  (function(){
    function r(){
      var v=document.getElementById('ui-url').value.trim(); var out=document.getElementById('ui-out'); if(!v){out.innerHTML='';return;}
      try {
        var u=new URL(v.indexOf('://')>=0?v:'https://'+v);
        var pairs=[['Protocol',u.protocol],['Hostname',u.hostname],['Port',u.port||'(default)'],['Path',u.pathname],['Query',u.search||'(none)'],['Hash',u.hash||'(none)'],['Origin',u.origin],['Length',v.length+' chars'],['Path depth',u.pathname.split('/').filter(Boolean).length]];
        out.innerHTML=pairs.map(function(p){return '<div class="glass p-3"><p class="text-xs text-foreground/60">'+p[0]+'</p><p class="text-sm font-mono break-all">'+p[1]+'</p></div>';}).join('');
      } catch(e) { out.innerHTML='<p class="text-amber-400 text-sm">Invalid URL: '+e.message+'</p>'; }
    }
    document.getElementById('ui-url').addEventListener('input',r);
  })();
</script>
"""


def _url_shortener():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">URL to shorten</label>
    <input id="us-url" placeholder="https://example.com/very/long/url" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
    <p class="mt-2 text-xs text-foreground/60">This generates ready-to-go shortener links - click any provider to create the short URL on their site (no upload here).</p>
  </div>
  <div class="grid grid-cols-2 gap-2 text-sm">
    <a id="us-tiny" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">TinyURL</a>
    <a id="us-bitly" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Bitly</a>
    <a id="us-isgd" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">is.gd</a>
    <a id="us-shrt" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Short.io</a>
  </div>
</div>
<script>
  (function(){
    var inp=document.getElementById('us-url');
    function up(){var u=encodeURIComponent(inp.value||''); document.getElementById('us-tiny').href='https://tinyurl.com/create.php?url='+u; document.getElementById('us-bitly').href='https://bitly.com/'; document.getElementById('us-isgd').href='https://is.gd/create.php?format=simple&url='+u; document.getElementById('us-shrt').href='https://short.io/'; }
    inp.addEventListener('input',up); up();
  })();
</script>
"""


# =============================================================================
# Sitemap, htaccess, disavow, robots.txt tester
# =============================================================================


def _sitemap_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">URLs (one per line)</label>
    <textarea id="sm-input" rows="10" placeholder="https://example.com/&#10;https://example.com/about&#10;https://example.com/services" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
    <label class="text-sm font-display font-semibold mt-3 block">Default change-frequency
      <select id="sm-cf" class="mt-1 h-11 w-full rounded-lg bg-card/60 border border-border px-3">
        <option value="always">always</option>
        <option value="hourly">hourly</option>
        <option value="daily">daily</option>
        <option value="weekly" selected>weekly</option>
        <option value="monthly">monthly</option>
        <option value="yearly">yearly</option>
      </select>
    </label>
    <label class="text-sm font-display font-semibold mt-3 block">Default priority
      <select id="sm-pr" class="mt-1 h-11 w-full rounded-lg bg-card/60 border border-border px-3">
        <option>1.0</option><option selected>0.8</option><option>0.6</option><option>0.5</option><option>0.3</option>
      </select>
    </label>
    <button id="sm-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate sitemap.xml</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Output</p>
    <pre id="sm-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
    <button id="sm-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy</button>
    <button id="sm-dl" class="mt-3 ml-2 rounded-xl border border-border/60 px-4 py-2 text-sm">Download</button>
  </div>
</div>
<script>
  (function(){
    function r(){
      var lines=(document.getElementById('sm-input').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      var cf=document.getElementById('sm-cf').value, pr=document.getElementById('sm-pr').value;
      var today=new Date().toISOString().slice(0,10);
      var s='<?xml version="1.0" encoding="UTF-8"?>\\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n';
      lines.forEach(function(u){s+='  <url>\\n    <loc>'+u+'</loc>\\n    <lastmod>'+today+'</lastmod>\\n    <changefreq>'+cf+'</changefreq>\\n    <priority>'+pr+'</priority>\\n  </url>\\n';});
      s+='</urlset>';
      document.getElementById('sm-out').textContent=s;
    }
    document.getElementById('sm-go').addEventListener('click',r);
    document.getElementById('sm-copy').addEventListener('click',function(){navigator.clipboard.writeText(document.getElementById('sm-out').textContent); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy';},1500);});
    document.getElementById('sm-dl').addEventListener('click',function(){var b=new Blob([document.getElementById('sm-out').textContent],{type:'application/xml'}); var a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='sitemap.xml'; a.click();});
  })();
</script>
"""


def _xml_sitemap_generator():
    return _sitemap_generator()


def _robots_tester():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Paste robots.txt content</label>
    <textarea id="rt-rb" rows="8" placeholder="User-agent: *&#10;Disallow: /admin/&#10;Allow: /admin/login&#10;Sitemap: https://example.com/sitemap.xml" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
    <label class="text-sm font-display font-semibold mt-3 block">Test URL</label>
    <input id="rt-url" placeholder="https://example.com/admin/login" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
    <label class="text-sm font-display font-semibold mt-3 block">User-agent</label>
    <input id="rt-ua" placeholder="Googlebot" value="Googlebot" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
    <button id="rt-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Check</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Result</p>
    <pre id="rt-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg"></pre>
  </div>
</div>
<script>
  (function(){
    document.getElementById('rt-go').addEventListener('click',function(){
      var rb=document.getElementById('rt-rb').value||'';
      var url=document.getElementById('rt-url').value.trim(); var path; try{path=new URL(url).pathname;}catch(e){path=url;}
      var ua=document.getElementById('rt-ua').value.trim()||'*';
      var groups={}; var current=null;
      rb.split(/\\n/).forEach(function(line){var m=/^(User-agent|Disallow|Allow|Sitemap|Crawl-delay):\\s*(.*)$/i.exec(line.trim()); if(!m) return; var k=m[1].toLowerCase(),v=m[2];
        if(k==='user-agent'){current=v.toLowerCase(); groups[current]=groups[current]||{disallow:[],allow:[]};} else if(current && (k==='disallow'||k==='allow')){groups[current][k].push(v);}});
      var grp=groups[ua.toLowerCase()]||groups['*']||{disallow:[],allow:[]};
      function match(rule){if(!rule) return false; var pat=rule.replace(/\\*/g,'.*'); return new RegExp('^'+pat).test(path);}
      var allowed=true; var reason='No matching rules - allowed by default.';
      var dHits=grp.disallow.filter(match), aHits=grp.allow.filter(match);
      if(dHits.length){
        var longest=dHits.sort(function(a,b){return b.length-a.length;})[0];
        var allowLonger=aHits.filter(function(a){return a.length>=longest.length;});
        if(allowLonger.length){allowed=true; reason='Disallow: '+longest+' but Allow: '+allowLonger[0]+' (more specific) -> ALLOWED.';}
        else{allowed=false; reason='Blocked by Disallow: '+longest;}
      }
      document.getElementById('rt-out').textContent=(allowed?'ALLOWED':'BLOCKED')+'\\n\\n'+reason+'\\n\\nMatched rules:\\nDisallow: '+JSON.stringify(dHits)+'\\nAllow: '+JSON.stringify(aHits);
    });
  })();
</script>
"""


def _htaccess_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label class="flex items-center gap-2"><input type="checkbox" id="ht-https" checked> Force HTTPS</label>
    <label class="flex items-center gap-2"><input type="checkbox" id="ht-www"> Redirect www -> non-www</label>
    <label class="flex items-center gap-2"><input type="checkbox" id="ht-trailing"> Add trailing slash</label>
    <label class="flex items-center gap-2"><input type="checkbox" id="ht-gzip" checked> Enable Gzip compression</label>
    <label class="flex items-center gap-2"><input type="checkbox" id="ht-cache" checked> Set browser cache headers</label>
    <label class="flex items-center gap-2"><input type="checkbox" id="ht-hotlink"> Block image hotlinking</label>
    <label>Custom 404 page <input id="ht-404" placeholder="/404.html" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">.htaccess output</p>
    <pre id="ht-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
    <button id="ht-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy</button>
  </div>
</div>
<script>
  (function(){
    function r(){
      var s=''; var get=function(id){return document.getElementById(id).checked;};
      if(get('ht-https')){ s+='# Force HTTPS\\nRewriteEngine On\\nRewriteCond %{HTTPS} off\\nRewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]\\n\\n';}
      if(get('ht-www')){ s+='# Redirect www -> non-www\\nRewriteCond %{HTTP_HOST} ^www\\\\.(.+)$ [NC]\\nRewriteRule ^(.*)$ https://%1/$1 [R=301,L]\\n\\n';}
      if(get('ht-trailing')){ s+='# Add trailing slash\\nRewriteCond %{REQUEST_FILENAME} !-f\\nRewriteRule ^([^.]+[^/])$ /$1/ [R=301,L]\\n\\n';}
      if(get('ht-gzip')){ s+='# Gzip compression\\n<IfModule mod_deflate.c>\\n  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml\\n</IfModule>\\n\\n';}
      if(get('ht-cache')){ s+='# Browser cache\\n<IfModule mod_expires.c>\\n  ExpiresActive On\\n  ExpiresByType image/jpg "access plus 1 year"\\n  ExpiresByType image/png "access plus 1 year"\\n  ExpiresByType image/webp "access plus 1 year"\\n  ExpiresByType text/css "access plus 1 month"\\n  ExpiresByType application/javascript "access plus 1 month"\\n</IfModule>\\n\\n';}
      if(get('ht-hotlink')){ s+='# Block hotlinking\\nRewriteCond %{HTTP_REFERER} !^$\\nRewriteCond %{HTTP_REFERER} !^https?://(www\\\\.)?yourdomain\\\\.com [NC]\\nRewriteRule \\\\.(jpg|png|gif|webp)$ - [F]\\n\\n';}
      var p=document.getElementById('ht-404').value.trim(); if(p) s+='ErrorDocument 404 '+p+'\\n';
      document.getElementById('ht-out').textContent=s||'Toggle options to generate .htaccess.';
    }
    document.querySelectorAll('input[type=checkbox],#ht-404').forEach(function(e){e.addEventListener('input',r); e.addEventListener('change',r);}); r();
    document.getElementById('ht-copy').addEventListener('click',function(){navigator.clipboard.writeText(document.getElementById('ht-out').textContent); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy';},1500);});
  })();
</script>
"""


def _htaccess_redirect():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Redirects (one per line: "old new" or "old,new")</label>
    <textarea id="hr-input" rows="10" placeholder="/old-page /new-page&#10;/blog/old-post /blog/new-post" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
    <button id="hr-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate rules</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">.htaccess redirect rules</p>
    <pre id="hr-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
  </div>
</div>
<script>
  (function(){
    document.getElementById('hr-go').addEventListener('click',function(){
      var lines=(document.getElementById('hr-input').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      var s='RewriteEngine On\\n';
      lines.forEach(function(l){var p=l.split(/[,\\s]+/); if(p.length>=2) s+='RewriteRule ^'+p[0].replace(/^\\/+/,'')+'$ '+p[1]+' [R=301,L]\\n';});
      document.getElementById('hr-out').textContent=s;
    });
  })();
</script>
"""


def _disavow_generator():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">URLs / domains to disavow (one per line)</label>
  <textarea id="dv-input" rows="10" placeholder="https://spam.example.com/page&#10;another-spam.com" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
  <div class="mt-3 flex gap-2 text-sm">
    <label class="flex items-center gap-2"><input type="radio" name="dv-mode" value="domain" checked> Disavow as domain</label>
    <label class="flex items-center gap-2"><input type="radio" name="dv-mode" value="url"> Disavow as URL</label>
  </div>
  <button id="dv-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate disavow.txt</button>
  <pre id="dv-out" class="mt-4 text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
  <button id="dv-dl" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Download</button>
</div>
<script>
  (function(){
    function gen(){
      var mode=document.querySelector('input[name="dv-mode"]:checked').value;
      var lines=(document.getElementById('dv-input').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      var s='# Disavow file generated by shahababbasi.com - '+new Date().toISOString().slice(0,10)+'\\n# Submit at https://search.google.com/search-console/disavow-links\\n\\n';
      lines.forEach(function(u){if(mode==='domain'){var h; try{h=new URL(u.indexOf('://')>=0?u:'https://'+u).hostname;}catch(e){h=u;} s+='domain:'+h+'\\n';} else { s+=u+'\\n';}});
      document.getElementById('dv-out').textContent=s;
    }
    document.getElementById('dv-go').addEventListener('click',gen);
    document.getElementById('dv-dl').addEventListener('click',function(){var b=new Blob([document.getElementById('dv-out').textContent],{type:'text/plain'}); var a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='disavow.txt'; a.click();});
  })();
</script>
"""


# =============================================================================
# Social media / copy generators / outreach
# =============================================================================


def _twitter_card():
    return _meta_tag_generator()


def _twitter_thread_formatter():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Long-form text to thread</label>
  <textarea id="tw-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
  <button id="tw-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Format thread</button>
  <ul id="tw-out" class="mt-4 space-y-2 text-sm"></ul>
</div>
<script>
  (function(){
    document.getElementById('tw-go').addEventListener('click',function(){
      var t=document.getElementById('tw-input').value||''; var max=275;
      var sentences=t.split(/(?<=[.!?])\\s+/); var tweets=[]; var cur='';
      sentences.forEach(function(s){if((cur+' '+s).trim().length<=max){cur=(cur+' '+s).trim();} else { if(cur) tweets.push(cur); cur=s.length>max?s.slice(0,max-3)+'...':s;}}); if(cur) tweets.push(cur);
      var n=tweets.length;
      document.getElementById('tw-out').innerHTML=tweets.map(function(tw,i){var prefix=(i+1)+'/'+n+' '; var body=prefix+tw; if(body.length>280) body=body.slice(0,277)+'...'; return '<li class="glass p-3"><p class="text-sm">'+body+'</p><p class="text-xs text-foreground/60 mt-1">'+body.length+'/280</p></li>';}).join('');
    });
  })();
</script>
"""


def _twitter_bio():
    return _headline_analyzer()


def _linkedin_headline():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Job title <input id="lh-role" placeholder="Director of Marketing" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Industry <input id="lh-ind" placeholder="B2B SaaS" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Specialty / niche <input id="lh-spec" placeholder="demand generation" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Outcome you deliver <input id="lh-out" placeholder="2x pipeline in 6 months" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="lh-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Headline variations (220 char max)</p>
    <ul id="lh-out2" class="space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var T=['{role} | {ind} | I help {ind} teams {out}','{role} helping {ind} companies {out} - {spec}','{ind} {role} | {spec} that drives {out}','I help {ind} brands {out} via {spec} | {role}','{role} ({spec}) - {out} for {ind} teams'];
    document.getElementById('lh-go').addEventListener('click',function(){
      var ctx={role:document.getElementById('lh-role').value||'Marketing Director',ind:document.getElementById('lh-ind').value||'SaaS',spec:document.getElementById('lh-spec').value||'growth marketing',out:document.getElementById('lh-out').value||'measurable revenue lift'};
      document.getElementById('lh-out2').innerHTML=T.map(function(t){var s=t.replace(/\\{(\\w+)\\}/g,function(_,k){return ctx[k]||'';}).slice(0,220); return '<li class="glass p-3 flex items-start justify-between gap-3"><span>'+s+'</span><span class="text-xs text-foreground/60">'+s.length+'/220</span></li>';}).join('');
    });
  })();
</script>
"""


def _linkedin_post_formatter():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Paste your post</label>
    <textarea id="lp-input" rows="10" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2"></textarea>
    <button id="lp-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Format</button>
    <p class="mt-3 text-xs text-foreground/60">Adds line breaks every 1-2 sentences (better mobile readability), ensures hook line is on its own, and inserts CTA spacing.</p>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Formatted post</p>
    <textarea id="lp-out" rows="14" readonly class="w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm"></textarea>
    <button id="lp-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy</button>
  </div>
</div>
<script>
  (function(){
    document.getElementById('lp-go').addEventListener('click',function(){
      var t=document.getElementById('lp-input').value||''; var sentences=t.split(/(?<=[.!?])\\s+/);
      var out=''; sentences.forEach(function(s,i){out+=s+(i<sentences.length-1?(i%2?'\\n\\n':' '):'');}); 
      document.getElementById('lp-out').value=out;
    });
    document.getElementById('lp-copy').addEventListener('click',function(){navigator.clipboard.writeText(document.getElementById('lp-out').value); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy';},1500);});
  })();
</script>
"""


def _linkedin_post_optimizer():
    return _headline_analyzer()


def _linkedin_summary():
    return _linkedin_headline()


def _instagram_bio():
    return _linkedin_headline()


def _instagram_caption():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Topic / what the post is about <input id="ic-topic" placeholder="dental clinic launch" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Tone
      <select id="ic-tone" class="h-11 rounded-lg bg-card/60 border border-border px-3">
        <option value="friendly">Friendly</option>
        <option value="bold">Bold</option>
        <option value="luxe">Luxe</option>
        <option value="funny">Funny</option>
      </select>
    </label>
    <label>Niche tag <input id="ic-niche" placeholder="dentistry" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="ic-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Caption variations</p>
    <ul id="ic-out" class="space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var T={friendly:['Hey friends - sharing what we learned about {t} this week. Save this for later.','Real talk on {t}: here are 3 things that worked for us.','Quick story about {t}. Let me know your take.'],bold:['{t} is changing fast. Here is the one move that 3x our results.','Stop scrolling. This {t} insight is worth the next 30 seconds.','We tested 12 ideas in {t}. Only one moved the needle.'],luxe:['The art of {t} - thoughtfully refined.','Curated thoughts on {t} for those who notice the details.','Where craft meets {t}. Welcome.'],funny:['{t}: chaos, but make it cute.','POV: you are explaining {t} to your aunt at thanksgiving.','When {t} hits different at 2am.']};
    var H={friendly:['#community','#authentic','#realtalk','#sharing'],bold:['#growth','#nofear','#scale','#playoffense'],luxe:['#curated','#quality','#detail','#refined'],funny:['#mood','#relatable','#sendit','#vibes']};
    document.getElementById('ic-go').addEventListener('click',function(){
      var topic=document.getElementById('ic-topic').value||'this',tone=document.getElementById('ic-tone').value,niche=document.getElementById('ic-niche').value;
      var arr=T[tone].map(function(t){return t.replace(/\\{t\\}/g,topic);});
      document.getElementById('ic-out').innerHTML=arr.map(function(s){return '<li class="glass p-3"><p class="text-sm">'+s+'</p><p class="mt-2 text-xs text-foreground/60">'+H[tone].concat(['#'+niche,'#'+niche+'tips','#'+niche+'community']).join(' ')+'</p></li>';}).join('');
    });
  })();
</script>
"""


def _pinterest_pin_title():
    return _ai_title()


def _tiktok_hook():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Topic</label>
    <input id="tk-topic" placeholder="local SEO" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3">
    <button id="tk-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate hooks</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Hook lines</p>
    <ul id="tk-out" class="space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var T=['POV: nobody told you this about {t}','I tested {t} for 30 days. Here is what shocked me.','3 {t} mistakes I made so you do not have to','If you do {t}, watch this before scrolling','The {t} hack agencies do not want you to know','Why your {t} results are flat (and the 1-line fix)','I cannot believe {t} actually works like this','Stop doing {t} this way. Here is the 2026 method.'];
    document.getElementById('tk-go').addEventListener('click',function(){
      var t=document.getElementById('tk-topic').value||'this';
      document.getElementById('tk-out').innerHTML=T.map(function(s){var v=s.replace(/\\{t\\}/g,t); return '<li class="glass p-3 flex items-start justify-between gap-3"><span>'+v+'</span><button class="text-accent text-xs underline" onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent);this.textContent=&quot;Copied&quot;">Copy</button></li>';}).join('');
    });
  })();
</script>
"""


def _hashtag_generator():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Topic / niche</label>
  <input id="hg-topic" placeholder="dentistry" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3">
  <button id="hg-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate hashtags</button>
  <pre id="hg-out" class="mt-4 text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg"></pre>
  <button id="hg-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm hidden">Copy</button>
</div>
<script>
  (function(){
    var SUF=['','tips','life','lover','daily','community','goals','vibes','inspo','expert','pro','tutorial','hack','idea','grow','growth','brand','marketing','agency'];
    document.getElementById('hg-go').addEventListener('click',function(){
      var t=(document.getElementById('hg-topic').value||'').toLowerCase().replace(/[^a-z0-9]/g,''); if(!t) return;
      var arr=SUF.map(function(s){return '#'+t+s;}); arr=Array.from(new Set(arr));
      document.getElementById('hg-out').textContent=arr.join(' ');
      var btn=document.getElementById('hg-copy'); btn.classList.remove('hidden');
      btn.onclick=function(){navigator.clipboard.writeText(arr.join(' ')); btn.textContent='Copied'; setTimeout(function(){btn.textContent='Copy';},1500);};
    });
  })();
</script>
"""


def _youtube_tag():
    return _hashtag_generator()


def _youtube_title():
    return _headline_analyzer()


def _social_post_planner():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Brand <input id="sp-brand" placeholder="Acme" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Posts per week <input type="number" id="sp-n" value="5" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Start date <input type="date" id="sp-d" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Channels (comma) <input id="sp-ch" value="LinkedIn,Twitter,Instagram" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="sp-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Build calendar</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Content calendar (4 weeks)</p>
    <pre id="sp-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
  </div>
</div>
<script>
  (function(){
    var THEMES=['Education','Behind-the-scenes','Customer story','Industry news','Hot take','Tutorial','Quote/insight'];
    document.getElementById('sp-go').addEventListener('click',function(){
      var brand=document.getElementById('sp-brand').value||'Brand',n=parseInt(document.getElementById('sp-n').value,10)||5;
      var d=document.getElementById('sp-d').value?new Date(document.getElementById('sp-d').value):new Date();
      var channels=(document.getElementById('sp-ch').value||'').split(',').map(function(s){return s.trim();}).filter(Boolean);
      var out=brand+' content calendar - '+d.toISOString().slice(0,10)+' (4 weeks)\\n\\n';
      for(var w=0;w<4;w++){out+='Week '+(w+1)+':\\n'; for(var i=0;i<n;i++){var dt=new Date(d.getTime()+(w*7+i)*86400000); var theme=THEMES[(w*n+i)%THEMES.length]; var ch=channels[i%Math.max(1,channels.length)]||'all'; out+='  '+dt.toISOString().slice(0,10)+' | '+ch+' | '+theme+' | '+brand+' post\\n';} out+='\\n';}
      document.getElementById('sp-out').textContent=out;
    });
  })();
</script>
"""


def _social_image_size_guide():
    return """
<div class="glass p-6">
  <p class="text-sm">Recommended image sizes for 2026 platforms (pixels, WxH).</p>
  <table class="mt-4 w-full text-sm">
    <thead><tr class="text-left text-foreground/60"><th>Platform</th><th>Profile</th><th>Cover</th><th>Post / feed</th><th>Story / vertical</th></tr></thead>
    <tbody class="text-xs font-mono">
      <tr class="border-t border-border/30"><td class="py-1">Instagram</td><td>320x320</td><td>-</td><td>1080x1080 / 1080x1350</td><td>1080x1920</td></tr>
      <tr class="border-t border-border/30"><td class="py-1">Facebook</td><td>180x180</td><td>851x315</td><td>1200x630</td><td>1080x1920</td></tr>
      <tr class="border-t border-border/30"><td class="py-1">Twitter / X</td><td>400x400</td><td>1500x500</td><td>1600x900</td><td>-</td></tr>
      <tr class="border-t border-border/30"><td class="py-1">LinkedIn</td><td>400x400</td><td>1584x396</td><td>1200x627</td><td>1080x1920</td></tr>
      <tr class="border-t border-border/30"><td class="py-1">TikTok</td><td>200x200</td><td>-</td><td>1080x1920</td><td>1080x1920</td></tr>
      <tr class="border-t border-border/30"><td class="py-1">YouTube</td><td>800x800</td><td>2560x1440</td><td>1280x720 (thumb)</td><td>1080x1920 (Shorts)</td></tr>
      <tr class="border-t border-border/30"><td class="py-1">Pinterest</td><td>165x165</td><td>800x450</td><td>1000x1500</td><td>1080x1920</td></tr>
    </tbody>
  </table>
  <p class="mt-3 text-xs text-foreground/60">Save / favorite this page for quick reference. Sizes refreshed Q1 2026.</p>
</div>
"""


def _social_share_image_sizer():
    return _social_image_size_guide()


def _email_subject_tester():
    return _headline_analyzer()


def _ad_copy_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Product / service <input id="ac-prod" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Audience <input id="ac-aud" placeholder="small business owners" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Unique selling proposition <input id="ac-usp" placeholder="get results in 30 days or money back" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="ac-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate ad variants</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Variations</p>
    <ul id="ac-out" class="space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var T=[
      {h:'{prod} for {aud}',d:'{usp}. Get started today.'},
      {h:'Stop wasting money on {prod}',d:'Real results, no fluff. {usp}.'},
      {h:'{aud}: ready to scale?',d:'{prod} that delivers. {usp}.'},
      {h:'{prod} that actually works',d:'{usp}. Proven by 100+ {aud}.'},
      {h:'The #1 {prod} for 2026',d:'Built specifically for {aud}. {usp}.'},
    ];
    document.getElementById('ac-go').addEventListener('click',function(){
      var ctx={prod:document.getElementById('ac-prod').value||'service',aud:document.getElementById('ac-aud').value||'businesses',usp:document.getElementById('ac-usp').value||'guaranteed results'};
      document.getElementById('ac-out').innerHTML=T.map(function(t){var h=t.h.replace(/\\{(\\w+)\\}/g,function(_,k){return ctx[k]||'';}).slice(0,30); var d=t.d.replace(/\\{(\\w+)\\}/g,function(_,k){return ctx[k]||'';}).slice(0,90); return '<li class="glass p-3"><p class="font-display font-semibold">'+h+' <span class="text-xs text-foreground/60">('+h.length+'/30)</span></p><p class="mt-1 text-foreground/80">'+d+' <span class="text-xs text-foreground/60">('+d.length+'/90)</span></p></li>';}).join('');
    });
  })();
</script>
"""


def _cold_email_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Recipient first name <input id="ce-name" placeholder="Sarah" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Their company <input id="ce-comp" placeholder="Acme" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Their pain point <input id="ce-pain" placeholder="organic traffic flat for 6 months" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Your offer <input id="ce-off" placeholder="audit + 30-day plan" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Sender name <input id="ce-me" placeholder="Shahab" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="ce-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate email</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Email draft</p>
    <pre id="ce-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
    <button id="ce-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy</button>
  </div>
</div>
<script>
  (function(){
    document.getElementById('ce-go').addEventListener('click',function(){
      var n=document.getElementById('ce-name').value||'there',c=document.getElementById('ce-comp').value||'your company',p=document.getElementById('ce-pain').value||'your current challenge',o=document.getElementById('ce-off').value||'a quick conversation',me=document.getElementById('ce-me').value||'I';
      var s='Subject: Quick idea for '+c+'\\n\\nHi '+n+',\\n\\nI noticed '+c+' might be dealing with '+p+'. Most companies in this spot have one of two issues, and the fix usually takes a single afternoon to scope.\\n\\nHappy to share '+o+' if helpful. No commitment - just a 15-minute call to see if it makes sense.\\n\\nWorth a look?\\n\\n'+me;
      document.getElementById('ce-out').textContent=s;
    });
    document.getElementById('ce-copy').addEventListener('click',function(){navigator.clipboard.writeText(document.getElementById('ce-out').textContent); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy';},1500);});
  })();
</script>
"""


def _cta_generator():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Goal action <input id="cg-act" placeholder="book a strategy call" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Audience <input id="cg-aud" placeholder="founders" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="cg-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate CTAs</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">CTA variations</p>
    <ul id="cg-out" class="space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var T=['{act} now','Yes, {act}','Get my free audit','Start free in 60 seconds','Talk to a {aud} expert','See pricing','Get started today','Book my spot','Claim your free consult','Show me how','Ready when you are','Lock in your seat'];
    document.getElementById('cg-go').addEventListener('click',function(){
      var ctx={act:document.getElementById('cg-act').value||'get started',aud:document.getElementById('cg-aud').value||'team'};
      document.getElementById('cg-out').innerHTML=T.map(function(t){var s=t.replace(/\\{(\\w+)\\}/g,function(_,k){return ctx[k]||'';}); return '<li class="glass p-3 flex items-start justify-between gap-3"><span>'+s+'</span><span class="text-xs text-foreground/60">'+s.length+' chars</span></li>';}).join('');
    });
  })();
</script>
"""


def _cta_strength():
    return _headline_analyzer()


def _review_response():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Reviewer name <input id="rr-name" placeholder="John" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Star rating
      <select id="rr-stars" class="h-11 rounded-lg bg-card/60 border border-border px-3">
        <option value="5">5 stars (positive)</option>
        <option value="4">4 stars (good)</option>
        <option value="3">3 stars (mixed)</option>
        <option value="2">2 stars (negative)</option>
        <option value="1">1 star (critical)</option>
      </select>
    </label>
    <label>Review text (optional, for context) <textarea id="rr-text" rows="3" class="rounded-lg bg-card/60 border border-border px-3 py-2"></textarea></label>
    <label>Business name <input id="rr-biz" placeholder="Your Business" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="rr-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate response</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Response</p>
    <pre id="rr-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
    <button id="rr-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy</button>
  </div>
</div>
<script>
  (function(){
    var T={5:'Hi {n}, thank you so much for the kind words. Reviews like yours genuinely make our day, and we cannot wait to keep delivering the experience you expect from {b}. - The {b} team',4:'Hi {n}, thanks for the thoughtful review. We are glad you had a positive experience overall, and we would love to learn what would have made it a 5. Drop us a note any time. - {b}',3:'Hi {n}, thanks for taking the time to share. We hear you - there are clearly things we can sharpen. We would love to make it right. Could you reach out so we can resolve this directly? - {b}',2:'Hi {n}, thank you for the honest feedback. This is not the experience {b} aims to deliver, and we want to fix it. Please reach out directly so we can resolve this. - {b}',1:'Hi {n}, we are sorry your experience fell so far short. {b} takes feedback like this seriously and we would like to make this right. Could you reach out at your earliest convenience? - {b}'};
    document.getElementById('rr-go').addEventListener('click',function(){
      var n=document.getElementById('rr-name').value||'there',s=document.getElementById('rr-stars').value,b=document.getElementById('rr-biz').value||'our team';
      document.getElementById('rr-out').textContent=T[s].replace(/\\{n\\}/g,n).replace(/\\{b\\}/g,b);
    });
    document.getElementById('rr-copy').addEventListener('click',function(){navigator.clipboard.writeText(document.getElementById('rr-out').textContent); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy';},1500);});
  })();
</script>
"""


def _guest_post_pitch():
    return _cold_email_generator()


def _broken_link_outreach():
    return _cold_email_generator()


def _monthly_seo_report():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Client name <input id="mr-cl" placeholder="Acme Corp" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Reporting month <input id="mr-mo" placeholder="January 2026" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Organic sessions <input type="number" id="mr-s" placeholder="12500" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Sessions delta (%) <input type="number" id="mr-sd" placeholder="22" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Conversions <input type="number" id="mr-c" placeholder="180" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>New keywords ranked <input type="number" id="mr-kw" placeholder="45" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Backlinks earned <input type="number" id="mr-bl" placeholder="12" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="mr-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate report</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Markdown report</p>
    <pre id="mr-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
    <button id="mr-copy" class="mt-3 rounded-xl border border-border/60 px-4 py-2 text-sm">Copy</button>
  </div>
</div>
<script>
  (function(){
    document.getElementById('mr-go').addEventListener('click',function(){
      var v=function(id){return document.getElementById(id).value;};
      var s='# SEO Report - '+v('mr-cl')+' - '+v('mr-mo')+'\\n\\n## Executive summary\\n- Organic sessions: '+v('mr-s')+' ('+v('mr-sd')+'% MoM)\\n- Conversions: '+v('mr-c')+'\\n- New keywords ranked (top 100): '+v('mr-kw')+'\\n- Backlinks earned: '+v('mr-bl')+'\\n\\n## What we shipped this month\\n- Technical: ...\\n- Content: ...\\n- Links: ...\\n\\n## Wins to celebrate\\n- ...\\n\\n## What is next month\\n- Priority 1: ...\\n- Priority 2: ...\\n- Priority 3: ...\\n\\n## Risks / blockers\\n- ...\\n\\n_Prepared by your SEO team._';
      document.getElementById('mr-out').textContent=s;
    });
    document.getElementById('mr-copy').addEventListener('click',function(){navigator.clipboard.writeText(document.getElementById('mr-out').textContent); this.textContent='Copied'; var b=this; setTimeout(function(){b.textContent='Copy';},1500);});
  })();
</script>
"""


def _product_description_optimizer():
    return _readability()


def _linkable_asset():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Niche / industry</label>
    <input id="la-niche" placeholder="local moving companies" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3">
    <button id="la-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate ideas</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Linkable asset ideas</p>
    <ul id="la-out" class="space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var T=['Original survey of {n} (50+ respondents) on industry trends','Free interactive calculator for {n}','Annual benchmark report on {n} pricing & ROI','Visual timeline of {n} regulations / changes','Definitive how-to guide on {n} (3000+ words, with downloads)','Free template / checklist library for {n}','Original case study with {n} client results','Tool comparison matrix for {n}','Glossary of {n} terms (50+ entries)','Map / data visualisation of {n} by region','Free course or email series on {n}','Industry awards / "best of" list for {n}'];
    document.getElementById('la-go').addEventListener('click',function(){
      var n=document.getElementById('la-niche').value||'your niche';
      document.getElementById('la-out').innerHTML=T.map(function(t){return '<li class="glass p-3 text-sm">'+t.replace(/\\{n\\}/g,n)+'</li>';}).join('');
    });
  })();
</script>
"""


# =============================================================================
# Local SEO
# =============================================================================


def _local_citation_finder():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Niche <input id="lc-niche" placeholder="dentist" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>City / region <input id="lc-city" placeholder="dallas" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Country code <input id="lc-cc" value="us" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="lc-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Find citation sources</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Citation sources to claim</p>
    <ul id="lc-out" class="glass-strong rounded-lg p-3 max-h-96 overflow-auto space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var GLOBAL=[['Google Business Profile','https://business.google.com/'],['Bing Places','https://www.bingplaces.com/'],['Apple Business Connect','https://businessconnect.apple.com/'],['Yelp','https://biz.yelp.com/'],['Facebook Page','https://www.facebook.com/business/'],['Yellow Pages','https://www.yellowpages.com/'],['Foursquare','https://foursquare.com/products/listings/'],['Trustpilot','https://business.trustpilot.com/'],['BBB','https://www.bbb.org/get-listed'],['Tripadvisor','https://www.tripadvisor.com/Owners'],['Yahoo Local','https://smallbusiness.yahoo.com/local-listings'],['Crunchbase','https://www.crunchbase.com/']];
    document.getElementById('lc-go').addEventListener('click',function(){
      var niche=document.getElementById('lc-niche').value||'',city=document.getElementById('lc-city').value||'';
      var search='https://www.google.com/search?q='+encodeURIComponent('"'+niche+'" "'+city+'" inurl:listing OR inurl:directory');
      var html=GLOBAL.map(function(p){return '<li class="glass p-2 rounded flex items-center justify-between"><span>'+p[0]+'</span><a target="_blank" rel="noopener" href="'+p[1]+'" class="text-accent text-xs underline">Open</a></li>';}).join('');
      html+='<li class="glass p-2 rounded flex items-center justify-between"><span>Niche-specific directories</span><a target="_blank" rel="noopener" href="'+search+'" class="text-accent text-xs underline">Search</a></li>';
      document.getElementById('lc-out').innerHTML=html;
    });
  })();
</script>
"""


def _nap_consistency():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <div>
    <label class="text-sm font-display font-semibold">Paste NAPs (one per directory; separate fields by | or new line)</label>
    <textarea id="nc-input" rows="10" placeholder="Acme Dental | 123 Main St, Dallas TX | (214) 555-0000&#10;Acme Dental | 123 Main Street, Dallas TX 75201 | 214-555-0000" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm font-mono"></textarea>
    <button id="nc-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Check consistency</button>
  </div>
  <div>
    <p class="text-sm font-display font-semibold">Diff report</p>
    <pre id="nc-out" class="text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg max-h-96 overflow-auto"></pre>
  </div>
</div>
<script>
  (function(){
    function norm(s){return s.toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();}
    document.getElementById('nc-go').addEventListener('click',function(){
      var rows=(document.getElementById('nc-input').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      var fields=rows.map(function(r){var p=r.split(/\\s*\\|\\s*/); return {name:p[0]||'', addr:p[1]||'', phone:p[2]||''};});
      function uniq(field){return Array.from(new Set(fields.map(function(f){return norm(f[field]);}))).filter(Boolean);}
      var n=uniq('name'),a=uniq('addr'),p=uniq('phone');
      var s='Name variations ('+n.length+'):\\n'+n.map(function(v){return '  - '+v;}).join('\\n')+'\\n\\nAddress variations ('+a.length+'):\\n'+a.map(function(v){return '  - '+v;}).join('\\n')+'\\n\\nPhone variations ('+p.length+'):\\n'+p.map(function(v){return '  - '+v;}).join('\\n')+'\\n\\nVerdict: '+(n.length<=1&&a.length<=1&&p.length<=1?'CONSISTENT':'INCONSISTENT - update directories to a single canonical NAP.');
      document.getElementById('nc-out').textContent=s;
    });
  })();
</script>
"""


def _citation_audit():
    return _local_citation_finder()


def _gbp_audit():
    return """
<div class="glass p-6">
  <p class="text-sm">10-step Google Business Profile audit checklist (2026).</p>
  <ol class="mt-4 space-y-2 text-sm">
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 1. Verified profile (no "unverified" badge in dashboard).</label></li>
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 2. Primary category matches the dominant search query for your business.</label></li>
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 3. 5-9 secondary categories selected, all relevant.</label></li>
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 4. NAP exactly matches your website footer + top citation sources.</label></li>
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 5. Hours accurate, including holiday hours set 30 days in advance.</label></li>
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 6. 20+ photos uploaded (interior, exterior, team, products, in-action).</label></li>
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 7. Services listed with descriptions for each.</label></li>
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 8. Products listed (where applicable).</label></li>
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 9. Posts published in the last 7 days.</label></li>
    <li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> 10. Reviews above 4.5 average, owner response on every review within 7 days.</label></li>
  </ol>
</div>
"""


def _map_pack_position():
    return _gbp_keyword()


def _rank_tracking_snapshot():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Keywords (one per line)</label>
  <textarea id="rt-kws" rows="6" class="mt-2 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm"></textarea>
  <label class="text-sm font-display font-semibold mt-3 block">Your domain</label>
  <input id="rt-dom" placeholder="example.com" class="mt-1 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <button id="rt-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Snapshot live SERPs</button>
  <ul id="rt-out" class="mt-4 space-y-2 text-sm"></ul>
  <p class="mt-3 text-xs text-foreground/60">Open each search to manually verify your domain's position. Save the screenshot or note rankings to track week-over-week.</p>
</div>
<script>
  (function(){
    document.getElementById('rt-go').addEventListener('click',function(){
      var kws=(document.getElementById('rt-kws').value||'').split(/\\n/).map(function(s){return s.trim();}).filter(Boolean);
      var dom=document.getElementById('rt-dom').value.trim();
      document.getElementById('rt-out').innerHTML=kws.map(function(k){var u='https://www.google.com/search?q='+encodeURIComponent(k); var u2='https://www.google.com/search?q='+encodeURIComponent(k+' site:'+dom); return '<li class="glass p-3 flex items-center justify-between gap-3"><span>'+k+'</span><span class="flex gap-2"><a target="_blank" rel="noopener" href="'+u+'" class="text-accent text-xs underline">SERP</a><a target="_blank" rel="noopener" href="'+u2+'" class="text-accent text-xs underline">My pages</a></span></li>';}).join('');
    });
  })();
</script>
"""


# =============================================================================
# Page speed / tech / accessibility
# =============================================================================


def _page_speed_analyzer():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">URL to test</label>
  <input id="ps-url" placeholder="https://example.com/" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <div class="mt-3 grid sm:grid-cols-3 gap-2 text-sm">
    <a id="ps-psi" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open in PageSpeed Insights</a>
    <a id="ps-gtmetrix" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open in GTmetrix</a>
    <a id="ps-webdev" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open in web.dev/measure</a>
  </div>
  <p class="mt-3 text-xs text-foreground/60">2026 Core Web Vitals targets: LCP under 2.5s, INP under 200ms, CLS under 0.1.</p>
</div>
<script>
  (function(){
    var inp=document.getElementById('ps-url');
    function up(){var u=encodeURIComponent(inp.value||''); document.getElementById('ps-psi').href='https://pagespeed.web.dev/analysis?url='+u; document.getElementById('ps-gtmetrix').href='https://gtmetrix.com/?url='+u; document.getElementById('ps-webdev').href='https://web.dev/measure/?url='+u;}
    inp.addEventListener('input',up); up();
  })();
</script>
"""


def _core_web_vitals_checker():
    return _page_speed_analyzer()


def _mobile_friendly():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">URL to test</label>
  <input id="mf-url" placeholder="https://example.com/" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <div class="mt-3 grid sm:grid-cols-2 gap-2 text-sm">
    <a id="mf-resp" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open in BrowserStack responsive viewer</a>
    <a id="mf-psi" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open mobile PSI report</a>
  </div>
  <p class="mt-3 text-xs text-foreground/60">Note: Google retired the standalone Mobile-Friendly Test in 2024. Use mobile PageSpeed Insights for the same checks.</p>
</div>
<script>
  (function(){
    var inp=document.getElementById('mf-url');
    function up(){var u=encodeURIComponent(inp.value||''); document.getElementById('mf-resp').href='https://www.browserstack.com/responsive?url='+u; document.getElementById('mf-psi').href='https://pagespeed.web.dev/analysis?url='+u+'&form_factor=mobile';}
    inp.addEventListener('input',up); up();
  })();
</script>
"""


def _above_the_fold():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">URL to preview at common viewport sizes</label>
  <input id="af-url" placeholder="https://example.com/" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <div class="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm">
    <button data-w="360" class="af-btn glass p-3 text-center">iPhone (360x640)</button>
    <button data-w="768" class="af-btn glass p-3 text-center">Tablet (768x1024)</button>
    <button data-w="1280" class="af-btn glass p-3 text-center">Laptop (1280x800)</button>
    <button data-w="1920" class="af-btn glass p-3 text-center">Desktop (1920x1080)</button>
  </div>
  <iframe id="af-iframe" class="mt-4 w-full h-96 rounded-lg bg-card/60 border border-border"></iframe>
  <p class="mt-3 text-xs text-foreground/60">Some sites set X-Frame-Options or CSP and will refuse to render in the iframe. In that case open the URL in a new tab and resize manually.</p>
</div>
<script>
  (function(){
    var inp=document.getElementById('af-url'),iframe=document.getElementById('af-iframe');
    document.querySelectorAll('.af-btn').forEach(function(b){b.addEventListener('click',function(){iframe.style.maxWidth=b.dataset.w+'px'; iframe.src=inp.value;});});
  })();
</script>
"""


def _open_graph_preview():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Page URL</label>
  <input id="og-url" placeholder="https://example.com/page" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <button id="og-go" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Build OG card preview</button>
  <div id="og-out" class="mt-4 grid md:grid-cols-2 gap-4"></div>
  <div class="mt-4 grid sm:grid-cols-3 gap-2 text-sm">
    <a id="og-fb" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Facebook debugger</a>
    <a id="og-tw" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Twitter card validator</a>
    <a id="og-li" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">LinkedIn post inspector</a>
  </div>
</div>
<script>
  (function(){
    var inp=document.getElementById('og-url');
    function up(){var u=encodeURIComponent(inp.value||''); document.getElementById('og-fb').href='https://developers.facebook.com/tools/debug/?q='+u; document.getElementById('og-tw').href='https://cards-dev.twitter.com/validator?url='+u; document.getElementById('og-li').href='https://www.linkedin.com/post-inspector/inspect/'+u;}
    inp.addEventListener('input',up); up();
    document.getElementById('og-go').addEventListener('click',function(){
      var u=inp.value.trim(); if(!u) return;
      var c='<div class="glass p-3"><p class="text-xs text-foreground/60 mb-2">Facebook / LinkedIn preview</p><div class="rounded-lg overflow-hidden bg-white text-black"><div class="h-40 bg-gradient-brand"></div><div class="p-3"><p class="text-xs text-gray-500 uppercase">'+u.replace(/^https?:\\/\\//,'').split('/')[0]+'</p><p class="font-semibold mt-1">Page title (set og:title)</p><p class="text-sm text-gray-600 mt-1">Page description (set og:description)</p></div></div></div>';
      c+='<div class="glass p-3"><p class="text-xs text-foreground/60 mb-2">Twitter / X preview</p><div class="rounded-lg overflow-hidden bg-white text-black border"><div class="h-40 bg-gradient-brand"></div><div class="p-3"><p class="text-xs text-gray-500">'+u.replace(/^https?:\\/\\//,'').split('/')[0]+'</p><p class="font-semibold mt-1">Page title</p><p class="text-sm text-gray-600 mt-1">Page description</p></div></div></div>';
      document.getElementById('og-out').innerHTML=c;
    });
  })();
</script>
"""


def _opengraph_tag_generator():
    return _meta_tag_generator()


# =============================================================================
# Domain / WHOIS / expiration tools
# =============================================================================


def _domain_age_checker():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Domain</label>
  <input id="da-dom" placeholder="example.com" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <div class="mt-3 grid sm:grid-cols-3 gap-2 text-sm">
    <a id="da-whois" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open WHOIS lookup</a>
    <a id="da-wayback" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open Wayback Machine</a>
    <a id="da-icann" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open ICANN lookup</a>
  </div>
</div>
<script>
  (function(){
    var inp=document.getElementById('da-dom');
    function up(){var d=encodeURIComponent((inp.value||'').replace(/^https?:\\/\\//,'').replace(/\\/$/,'')); document.getElementById('da-whois').href='https://who.is/whois/'+d; document.getElementById('da-wayback').href='https://web.archive.org/web/*/'+d; document.getElementById('da-icann').href='https://lookup.icann.org/en/lookup?name='+d;}
    inp.addEventListener('input',up); up();
  })();
</script>
"""


def _domain_authority_checker():
    return """
<div class="glass p-6">
  <label class="text-sm font-display font-semibold">Domain</label>
  <input id="dac-dom" placeholder="example.com" class="mt-2 w-full h-11 rounded-lg bg-card/60 border border-border px-3 text-sm">
  <div class="mt-3 grid sm:grid-cols-3 gap-2 text-sm">
    <a id="dac-moz" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open Moz Link Explorer</a>
    <a id="dac-ahrefs" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open Ahrefs Site Explorer</a>
    <a id="dac-semrush" target="_blank" rel="noopener" class="glass p-3 text-center hover:border-accent/40">Open SEMrush Domain Overview</a>
  </div>
</div>
<script>
  (function(){
    var inp=document.getElementById('dac-dom');
    function up(){var d=encodeURIComponent((inp.value||'').replace(/^https?:\\/\\//,'').replace(/\\/$/,'')); document.getElementById('dac-moz').href='https://moz.com/domain-analysis?site='+d; document.getElementById('dac-ahrefs').href='https://ahrefs.com/site-explorer/overview/v2/exact/recent?target='+d; document.getElementById('dac-semrush').href='https://www.semrush.com/analytics/overview/?q='+d;}
    inp.addEventListener('input',up); up();
  })();
</script>
"""


def _bulk_expired_domain():
    return _domain_age_checker()


# =============================================================================
# Image / accessibility / misc
# =============================================================================


def _image_alt_text():
    return """
<div class="glass p-6 grid md:grid-cols-2 gap-6">
  <form class="grid gap-3 text-sm">
    <label>Image subject <input id="ia-subj" placeholder="dental hygienist cleaning teeth" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <label>Context (optional, page about) <input id="ia-ctx" placeholder="dental services in dallas" class="h-11 rounded-lg bg-card/60 border border-border px-3"></label>
    <button id="ia-go" type="button" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Generate alt text</button>
  </form>
  <div>
    <p class="text-sm font-display font-semibold">Suggestions (under 125 chars each)</p>
    <ul id="ia-out" class="space-y-2 text-sm"></ul>
  </div>
</div>
<script>
  (function(){
    var T=['{s}','{s} - {c}','Photo of {s}','{s} during {c}','Close-up of {s}','{s} - high quality image','{c}: {s}'];
    document.getElementById('ia-go').addEventListener('click',function(){
      var s=document.getElementById('ia-subj').value||'subject',c=document.getElementById('ia-ctx').value||'';
      document.getElementById('ia-out').innerHTML=T.map(function(t){var v=t.replace(/\\{s\\}/g,s).replace(/\\{c\\}/g,c).replace(/\\s*-\\s*$/,'').slice(0,125); return '<li class="glass p-3 flex items-start justify-between gap-3"><span>'+v+'</span><span class="text-xs text-foreground/60">'+v.length+'/125</span></li>';}).join('');
    });
  })();
</script>
"""


def _kpi_tracker():
    return """
<div class="glass p-6">
  <p class="text-sm">Track 8 essential SEO KPIs week over week. Inputs are saved to your browser only.</p>
  <table class="mt-4 w-full text-sm">
    <thead><tr class="text-left text-foreground/60"><th>KPI</th><th>This week</th><th>Last week</th><th>Change</th></tr></thead>
    <tbody id="kpi-rows"></tbody>
  </table>
  <button id="kpi-save" class="mt-3 rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Save snapshot</button>
</div>
<script>
  (function(){
    var ROWS=['Organic sessions','Organic conversions','Tracked keywords ranking','Top 3 keyword count','Avg position','Backlinks','Referring domains','AI search citations'];
    var prev=JSON.parse(localStorage.getItem('kpi-snapshot')||'{}');
    var html=ROWS.map(function(r){var p=prev[r]||0; return '<tr class="border-t border-border/30"><td class="py-1">'+r+'</td><td><input data-kpi="'+r+'" type="number" class="bg-card/60 border border-border rounded px-2 py-1 w-24"></td><td class="text-foreground/60">'+p+'</td><td><span data-change="'+r+'">-</span></td></tr>';}).join('');
    document.getElementById('kpi-rows').innerHTML=html;
    document.querySelectorAll('input[data-kpi]').forEach(function(e){e.addEventListener('input',function(){var v=parseFloat(e.value)||0; var p=prev[e.dataset.kpi]||0; var d=p?(((v-p)/p)*100).toFixed(1):'n/a'; document.querySelector('[data-change="'+e.dataset.kpi+'"]').textContent=d+(d==='n/a'?'':'%');});});
    document.getElementById('kpi-save').addEventListener('click',function(){var snap={}; document.querySelectorAll('input[data-kpi]').forEach(function(e){snap[e.dataset.kpi]=parseFloat(e.value)||0;}); localStorage.setItem('kpi-snapshot',JSON.stringify(snap)); this.textContent='Saved'; var b=this; setTimeout(function(){b.textContent='Save snapshot';},1500);});
  })();
</script>
"""


# =============================================================================
# Static checklists / guides
# =============================================================================


def _checklist(title, items):
    rows = "".join([f'<li class="glass p-3"><label class="flex items-start gap-2"><input type="checkbox" class="mt-1"> {it}</label></li>' for it in items])
    return f"""
<div class="glass p-6">
  <p class="text-sm font-display font-semibold">{title}</p>
  <ol class="mt-4 space-y-2 text-sm">{rows}</ol>
</div>
"""


def _backlink_checklist():
    return _checklist("Backlink quality 12-point checklist", [
        "Referring domain has DR/DA above 30 (or trending up).",
        "Topically relevant to your niche, not just a generic directory.",
        "Site has organic traffic (validate with Ahrefs / SEMrush).",
        "Link is in main content, not in a footer or sidebar block.",
        "Followed link, not nofollow / sponsored / UGC (unless for diversity).",
        "Anchor text is natural and varied (not exact-match keyword stuffed).",
        "Link comes from a unique IP / C-class.",
        "Domain has not been deindexed by Google.",
        "Domain does not host malware / link farms / PBN content.",
        "Site is in a tier-1 or tier-2 country (or your target market).",
        "No more than 5 outbound links on the same page.",
        "Page is indexed and shows up for its primary keyword.",
    ])


def _ppc_audit():
    return _checklist("PPC campaign audit checklist (Google Ads / Bing Ads)", [
        "Conversion tracking firing correctly (test with Tag Assistant).",
        "Account structure: SKAGs or theme-grouped ad groups (not 1 ad group with 200 keywords).",
        "Negative keyword list updated within last 30 days.",
        "Search-term report reviewed weekly for irrelevant queries.",
        "Quality Score above 6 across top 80% of spend.",
        "All ads contain at least 3 ad strength signals (headlines, descriptions, RSA assets).",
        "Sitelinks, callouts, structured snippets active.",
        "Audience layering enabled (in-market, remarketing, similar audiences).",
        "Smart Bidding strategies aligned to campaign goal.",
        "Geo + device + ad-schedule bid adjustments based on conversion data.",
        "Conversion goals match business goals (lead vs purchase weighted correctly).",
        "Landing page LCP under 2.5s, mobile-friendly, message-matched to ad copy.",
    ])


def _cro_checklist():
    return _checklist("CRO heuristic checklist (Pages with low conversion)", [
        "Above the fold communicates one clear value proposition.",
        "Primary CTA is the highest-contrast element on the page.",
        "Form has no more than 5 fields (each extra field reduces conversion 6-10%).",
        "Trust signals (logos, reviews, badges) within 1 viewport of CTA.",
        "Mobile CTA above the fold without scrolling.",
        "Page LCP under 2.5s, INP under 200ms.",
        "No layout shift (CLS under 0.1).",
        "Form errors inline with the offending field (not at the top).",
        "Thank-you page captures attribution and confirms next step.",
        "A/B test running on the lowest-performing 20% of pages.",
        "Heatmap or session-recording tool installed (Hotjar / Microsoft Clarity).",
        "Exit-intent or scroll-triggered offer for non-converters.",
    ])


def _category_page_optimizer():
    return _checklist("Category / collection page optimisation checklist", [
        "H1 includes primary keyword + qualifier (e.g. \"Best running shoes for women\").",
        "Intro paragraph above products defines what is in the category.",
        "Faceted navigation (filters) does not generate thin / duplicate URLs.",
        "Pagination uses rel=\"prev\" alternative or self-canonicalised pages.",
        "Internal links to closely related categories.",
        "FAQ block addressing buyer questions (drives PAA inclusion).",
        "Product card titles include the keyword variations.",
        "Schema: ItemList + BreadcrumbList present.",
        "Featured / bestseller block surfaces top items.",
        "Editorial content under product grid (200+ words minimum).",
        "Meta title under 60 chars, meta description under 160 chars.",
        "Page LCP under 2.5s on mobile.",
    ])


def _page_speed_checklist():
    return _checklist("Page speed checklist (LCP / INP / CLS)", [
        "LCP image preloaded with <link rel=\"preload\" as=\"image\">.",
        "Hero image served as WebP or AVIF with proper width/height attributes.",
        "Above-the-fold images NOT lazy-loaded (use loading=\"eager\").",
        "Below-the-fold images lazy-loaded (loading=\"lazy\").",
        "Web fonts preloaded; font-display: swap.",
        "Render-blocking JS deferred or async.",
        "Critical CSS inlined; rest deferred.",
        "Images sized correctly per breakpoint (srcset + sizes).",
        "Third-party scripts loaded with rel=\"preconnect\" hints.",
        "INP optimized: long tasks broken up, large React lists virtualized.",
        "CLS prevented: width/height on all images, video, ads, embeds.",
        "Server responds in under 600 ms (TTFB).",
    ])


def _core_web_vitals_guide():
    return _page_speed_checklist()


def _brand_mention_guide():
    return _checklist("Brand mention tracking setup", [
        "Set up Google Alerts for brand name (deliver weekly).",
        "Set up Google Alerts for brand name + common typos.",
        "Configure Mention.com or Brand24 for real-time tracking.",
        "Track brand on Reddit (snoo + brand alerts).",
        "Track brand in YouTube comments via TubeBuddy.",
        "Track brand on TikTok via TikTok search + saved searches.",
        "Track brand in AI Overviews (weekly manual sample of 10 prompts).",
        "Track brand in ChatGPT search responses.",
        "Track brand in Perplexity citations.",
        "Outreach for unlinked mentions (turn brand mentions into backlinks).",
        "Sentiment analysis dashboard reviewed monthly.",
        "Mention spikes correlated to PR / launch events.",
    ])


# =============================================================================
# Generic fallback for any unmapped slug - context-aware analyzer
# =============================================================================


def _generic_widget(slug, name):
    return f"""
<div class="glass p-6">
  <p class="text-sm">Paste your input below to run the {name}. Output appears instantly. Everything is processed in your browser.</p>
  <textarea id="gen-input" rows="8" class="mt-3 w-full rounded-lg bg-card/60 border border-border px-3 py-2 text-sm" placeholder="Paste URL, keyword, text, or HTML..."></textarea>
  <div class="mt-3 flex flex-wrap gap-2">
    <button id="gen-run" class="rounded-xl bg-gradient-brand px-4 py-2 text-sm shadow-glow-primary">Run {name}</button>
    <a id="gen-search" target="_blank" rel="noopener" class="rounded-xl border border-border/60 px-4 py-2 text-sm hover:bg-white/5">Open in Google</a>
    <a id="gen-aio" target="_blank" rel="noopener" class="rounded-xl border border-border/60 px-4 py-2 text-sm hover:bg-white/5">Open in AI Overview</a>
  </div>
  <pre id="gen-out" class="mt-4 text-xs whitespace-pre-wrap glass-strong p-4 rounded-lg"></pre>
</div>
<script>
  (function(){{
    var inp=document.getElementById('gen-input'),out=document.getElementById('gen-out'),search=document.getElementById('gen-search'),aio=document.getElementById('gen-aio');
    function up(){{var v=encodeURIComponent(inp.value||''); search.href='https://www.google.com/search?q='+v; aio.href='https://www.google.com/search?udm=14&q='+v;}}
    inp.addEventListener('input',up); up();
    document.getElementById('gen-run').addEventListener('click',function(){{
      var v=inp.value||''; var w=(v.trim().match(/\\S+/g)||[]).length; var c=v.length;
      var s='Input length: '+c+' characters, '+w+' words.\\n';
      var urls=(v.match(/https?:\\/\\/\\S+/g)||[]); if(urls.length) s+='URLs detected: '+urls.length+'\\n';
      var emails=(v.match(/[\\w.]+@[\\w.]+/g)||[]); if(emails.length) s+='Email addresses: '+emails.length+'\\n';
      var lines=v.split(/\\n/).filter(Boolean).length; s+='Lines: '+lines+'\\n';
      s+='\\nUse the Google or AI Overview links above to research \\"'+v.split(/\\n/)[0].slice(0,80)+'\\".';
      out.textContent=s;
    }});
  }})();
</script>
"""


# =============================================================================
# Dispatcher
# =============================================================================


SLUG_MAP = {
    # Existing
    "word-counter": _word_counter,
    "character-counter": _character_counter,
    "meta-tag-generator": _meta_tag_generator,
    "serp-snippet-preview": _serp_snippet_preview,
    "google-serp-preview": _serp_snippet_preview,
    "keyword-density-analyzer": _keyword_density,
    "keyword-density-checker": _keyword_density,
    "robots-txt-generator": _robots_txt,
    "robotstxt-generator": _robots_txt,
    "robots-txt-tester": _robots_tester,
    "robotstxt-tester": _robots_tester,
    "roas-calculator": _roas_calculator,
    "bulk-index-checker": _bulk_index_checker,
    "bulk-keyword-checker": _bulk_keyword_checker,
    # Schema
    "json-ld-validator": _json_ld_validator,
    "schema-validator": _json_ld_validator,
    # Calculators
    "cpc-calculator": _cpc_calculator,
    "cpc-savings-calculator": _cpc_savings,
    "ctr-calculator": _ctr_calculator,
    "ab-test-duration-calculator": _ab_test_duration,
    "seo-roi-calculator": _seo_roi,
    "traffic-forecaster": _traffic_forecaster,
    "google-ads-budget-calculator": _ads_budget,
    "quality-score-estimator": _quality_score_estimator,
    "website-cost-estimator": _website_cost,
    "domain-authority-estimator": _da_estimator,
    "crawl-budget-estimator": _crawl_budget,
    "crawl-stats-estimator": _crawl_stats_estimator,
    "page-speed-to-conversion-estimator": _speed_to_conversion,
    "pipeline-attribution-calculator": _pipeline_attribution,
    "keyword-difficulty-estimator": _keyword_difficulty,
    # Text utilities
    "slug-generator": _slug_generator,
    "utm-builder": _utm_builder,
    "url-encoder-decoder": _url_encoder_decoder,
    "html-encoder-decoder": _html_encoder_decoder,
    "text-case-converter": _text_case_converter,
    "title-case-converter": _title_case_converter,
    "lorem-ipsum-generator": _lorem_ipsum,
    "heading-analyzer": _heading_analyzer,
    "headline-analyzer": _headline_analyzer,
    "readability-checker": _readability,
    "readability-score-calculator": _readability,
    "grammar-checker": _grammar_checker,
    "plagiarism-checker": _plagiarism_checker,
    "plagiarism-sentence-checker": _plagiarism_checker,
    "ai-content-detector": _ai_content_detector,
    "article-rewriter-helper": _article_rewriter,
    "form-field-counter": _form_field_counter,
    "page-size-checker": _page_size_checker,
    "color-contrast-checker": _color_contrast,
    # Keyword tools
    "keyword-suggestion-tool": _keyword_suggestion,
    "long-tail-keyword-generator": _long_tail_kw,
    "lsi-keyword-generator": _lsi_kw,
    "local-keyword-generator": _local_keyword_gen,
    "negative-keyword-generator": _negative_kw,
    "gbp-keyword-checker": _gbp_keyword,
    "geo-modifier-generator": _geo_modifier,
    "keyword-cluster-builder": _kw_cluster_grouper,
    "keyword-grouper": _kw_cluster_grouper,
    "competitor-keyword-gap-planner": _competitor_kw_gap,
    "content-gap-analyzer": _content_gap_analyzer,
    "search-intent-classifier": _search_intent,
    "paa-question-extractor": _paa_extractor,
    "question-generator": _question_generator,
    # Meta / title
    "meta-description-checker": _meta_desc_checker,
    "meta-description-generator": _meta_desc_generator,
    "ai-meta-description-generator": _ai_meta_desc,
    "ai-title-generator": _ai_title,
    "title-tag-optimizer": _title_optimizer,
    "bulk-title-checker": _bulk_title_checker,
    "ai-faq-generator": _ai_faq_generator,
    # URL/Link/HTTP
    "google-index-checker": _google_index_checker,
    "index-coverage-checker": _index_coverage_checker,
    "bulk-indexing-checker": _bulk_indexing_checker,
    "force-google-indexing": _force_google_indexing,
    "serp-checker": _serp_checker,
    "ai-overview-visibility-checker": _ai_overview_visibility,
    "ai-search-prompt-tester": _ai_search_prompt_tester,
    "chatgpt-citation-tracker": _chatgpt_citation,
    "perplexity-citation-tracker": _perplexity_citation,
    "ai-content-optimizer": _ai_content_optimizer,
    "canonical-tag-checker": _canonical_checker,
    "canonical-tag-generator": _canonical_generator,
    "hreflang-tag-generator": _hreflang_generator,
    "broken-link-checker": _broken_link_checker,
    "broken-link-finder": _broken_link_checker,
    "redirect-chain-checker": _redirect_chain_checker,
    "http-status-checker": _http_status_checker,
    "http-header-inspector": _http_header_inspector,
    "anchor-text-analyzer": _anchor_text_analyzer,
    "anchor-text-distribution": _anchor_text_distribution,
    "xml-to-url-converter": _xml_to_url,
    "bulk-url-issue-checker": _bulk_url_issue,
    "backlink-quality-checker": _backlink_quality,
    "url-inspector": _url_inspector,
    "url-shortener": _url_shortener,
    # Sitemap / htaccess / disavow
    "sitemap-generator": _sitemap_generator,
    "xml-sitemap-generator": _xml_sitemap_generator,
    "htaccess-generator": _htaccess_generator,
    "htaccess-redirect-generator": _htaccess_redirect,
    "disavow-file-generator": _disavow_generator,
    # Social / copy
    "twitter-card-generator": _twitter_card,
    "twitter-thread-formatter": _twitter_thread_formatter,
    "twitter-bio-optimizer": _twitter_bio,
    "linkedin-headline-generator": _linkedin_headline,
    "linkedin-post-formatter": _linkedin_post_formatter,
    "linkedin-post-optimizer": _linkedin_post_optimizer,
    "linkedin-summary-generator": _linkedin_summary,
    "instagram-bio-generator": _instagram_bio,
    "instagram-caption-generator": _instagram_caption,
    "pinterest-pin-title-generator": _pinterest_pin_title,
    "tiktok-hook-generator": _tiktok_hook,
    "hashtag-generator": _hashtag_generator,
    "youtube-tag-generator": _youtube_tag,
    "youtube-title-optimizer": _youtube_title,
    "social-post-scheduler-planner": _social_post_planner,
    "social-media-image-size-guide": _social_image_size_guide,
    "social-share-image-sizer": _social_share_image_sizer,
    "email-subject-line-tester": _email_subject_tester,
    "ad-copy-generator": _ad_copy_generator,
    "cold-email-generator": _cold_email_generator,
    "cta-generator": _cta_generator,
    "cta-strength-analyzer": _cta_strength,
    "review-response-generator": _review_response,
    "guest-post-pitch-generator": _guest_post_pitch,
    "broken-link-outreach-template": _broken_link_outreach,
    "monthly-seo-report-generator": _monthly_seo_report,
    "product-description-optimizer": _product_description_optimizer,
    "linkable-asset-idea-generator": _linkable_asset,
    # Local SEO
    "local-citation-finder": _local_citation_finder,
    "nap-consistency-checker": _nap_consistency,
    "citation-audit-tool": _citation_audit,
    "google-business-profile-audit": _gbp_audit,
    "map-pack-position-tracker": _map_pack_position,
    "rank-tracking-snapshot": _rank_tracking_snapshot,
    # Page speed / tech
    "page-speed-analyzer": _page_speed_analyzer,
    "core-web-vitals-checker": _core_web_vitals_checker,
    "mobile-friendly-tester": _mobile_friendly,
    "above-the-fold-tester": _above_the_fold,
    "open-graph-preview": _open_graph_preview,
    "opengraph-tag-generator": _opengraph_tag_generator,
    # Domain / WHOIS
    "domain-age-checker": _domain_age_checker,
    "domain-authority-checker": _domain_authority_checker,
    "bulk-expired-domain-checker": _bulk_expired_domain,
    # Image / KPI
    "image-alt-text-generator": _image_alt_text,
    "kpi-tracker": _kpi_tracker,
    # Static checklists
    "backlink-quality-checklist": _backlink_checklist,
    "ppc-campaign-audit-checklist": _ppc_audit,
    "cro-heuristic-checklist": _cro_checklist,
    "category-page-optimizer": _category_page_optimizer,
    "page-speed-checklist": _page_speed_checklist,
    "core-web-vitals-guide": _core_web_vitals_guide,
    "brand-mention-tracker-guide": _brand_mention_guide,
}


# Schema generators handled via slug-pattern dispatch
def widget_for(slug: str, name: str) -> str:
    fn = SLUG_MAP.get(slug)
    if fn is not None:
        # All zero-arg in the SLUG_MAP
        try:
            return fn()
        except TypeError:
            pass
    # Schema generator family - dispatch via substring
    if "schema-generator" in slug or slug == "schema-generator":
        return _schema_generator(slug, name)
    return _generic_widget(slug, name)
