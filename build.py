#!/usr/bin/env python3
"""Build passyourmississippicontractorexam.com (design: River Steel) into dist/.

Input: data/products-raw.json (Shopify collection 415587981), tools/mscopy.py, assets/.
Output: static HTML with JSON-LD, sitemap, robots, llms.txt, agents.md.
"""
import html, json, os, re, shutil, sys
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))
from msclass import classify, ptype, clean_sentences
import schemakit
from mscopy import *
ICONS = json.load(open(os.path.join(os.path.dirname(__file__), "tools", "icons.json")))


def icon(c, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS.get(c, ICONS["code-books-and-courses"])}</svg>')

CFG = json.load(open("site-config.json"))
SITE = CFG["siteUrl"].rstrip("/")
BRAND = CFG["brand"]
PHONE, PHONE_TEL, EMAIL = CFG["phone"], CFG["phoneTel"], CFG["email"]
OUT = "."  # GitHub Pages serves the repo root, like the other 1 Exam Prep sites
STATE_NAME = "Mississippi"
BLOG_URLS = []
SRC_CORE = [("Mississippi State Board of Contractors", MSBOC), ("MSBOC testing information", MSBOC_TESTING)]
STOP = {"the", "and", "for", "of", "on", "with", "to", "a", "an", "in", "by", "from", "based", "includes"}
e = lambda s: html.escape(str(s), quote=True)


def money(x):
    x = float(x)
    return f"${x:,.0f}" if x == int(x) else f"${x:,.2f}"


def slugify(s, maxlen=70):
    s = s.lower().replace("&", " ").replace("’", "").replace("'", "")
    words = [w for w in re.split(r"[^a-z0-9]+", s) if w and w not in STOP and w != "mississippi"]
    out = ""
    for w in words:
        if len(out) + len(w) + 1 > maxlen:
            break
        out = f"{out}-{w}" if out else w
    return out


def words(text):
    return len(re.findall(r"[A-Za-z0-9$%][\w$%,.'’-]*", text))


# ---------------------------------------------------------------- products
raw = json.load(open("data/products-raw.json"))
products, by_class, used = [], defaultdict(list), set()
for p in raw:
    if p["status"] != "ACTIVE":
        continue
    c = classify(p["title"])
    tkey, tlabel, torder = ptype(p["title"])
    slug = slugify(p["title"].replace("Mississippi", ""))
    base, n = slug, 2
    while (c, slug) in used:
        slug, n = f"{base}-{n}", n + 1
    used.add((c, slug))
    v = p["variants"]["nodes"][0]
    img = (p.get("featuredMedia") or {}).get("preview", {}).get("image") or {}
    lo = float(p["priceRangeV2"]["minVariantPrice"]["amount"])
    hi = float(p["priceRangeV2"]["maxVariantPrice"]["amount"])
    cmp = (p.get("compareAtPriceRange") or {}).get("maxVariantCompareAtPrice", {}) or {}
    item = dict(
        title=p["title"].strip(), handle=p["handle"], cls=c, slug=slug, tkey=tkey, tlabel=tlabel, torder=torder,
        lo=lo, hi=hi, compare=float(cmp.get("amount") or 0), variant=v["legacyResourceId"], sku=v.get("sku") or v["legacyResourceId"],
        img=img.get("url"), alt=(img.get("altText") or p["title"]).strip(), desc=p.get("description") or "",
        shop=p.get("onlineStoreUrl") or f"https://1examprep.com/products/{p['handle']}",
        ms="mississippi" in p["title"].lower(),
    )
    item["url"] = f"/{c}/{slug}/"
    products.append(item)
    by_class[c].append(item)
for c in by_class:
    by_class[c].sort(key=lambda x: (x["torder"], -x["lo"], x["title"]))

unclassified = [x["title"] for x in by_class.get("code-books-and-courses", [])]
print("Unclassified (code-books-and-courses):", *unclassified, sep="\n  ")


def cls_url(c):
    return f"/{c}/"


def cls_name(c):
    return CLASSES[c]["name"]


# ---------------------------------------------------------------- shared chrome
FONTS = "https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,500;0,600;0,700;0,800;1,800&family=Poppins:ital,wght@0,400;0,500;0,600;1,400&display=swap"


def head(title, desc, path, ld, og_img="/assets/logo.png", extra=""):
    canon = SITE + path
    blocks = "\n".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in ld)
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(BRAND)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img if og_img.startswith('http') else SITE + og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og_img if og_img.startswith('http') else SITE + og_img}">
<meta name="theme-color" content="#16302B">
<link rel="icon" href="/assets/favicon.ico" sizes="any">
<link rel="icon" href="/assets/favicon-48.png" type="image/png" sizes="48x48">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/site.css">
{extra}<script src="/assets/site.js" defer></script>
{blocks}
</head>
<body>
"""


def header():
    return f"""<header class="top" data-shrink>
  <div class="wrap top-in">
    <a class="brand" href="/"><img class="logo" src="/assets/logo-nav-light.png" width="217" height="56" alt="Pass Your Mississippi Contractor Exam"></a>
    <nav class="nav" aria-label="Main">
      <a href="/#find-your-license">Licenses</a>
      <a href="/how-to-get-licensed/">How to get licensed</a>
      <a href="/business-and-law/">Law and Business exam</a>
      <a href="/blog/">Blog</a>
      <a href="/faq/">FAQ</a>
      <a href="/reviews/">Reviews</a>
      <a href="/contact/">Contact</a>
    </nav>
    <a class="call" href="tel:{PHONE_TEL}">{PHONE}</a>
  </div>
</header>
"""


def footer():
    groups = []
    for g, gname, _ in GROUPS:
        cs = [c for c in CLASSES if CLASSES[c]["group"] == g and by_class.get(c)][:7]
        links = "".join(f'<li><a href="{cls_url(c)}">{e(cls_name(c))}</a></li>' for c in cs)
        groups.append(f"<div><p class=\"f-h\">{e(gname)}</p><ul>{links}</ul></div>")
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="f-river" aria-hidden="true"></div>
    <div class="f-grid">
      <div class="f-brand">
        <a class="brand" href="/"><img class="logo" src="/assets/logo-nav-light.png" width="217" height="56" alt="Pass Your Mississippi Contractor Exam"></a>
        <p>{e(CFG['tagline'])}</p>
        <p>Orders ship from 1 Exam Prep. Call <a href="tel:{PHONE_TEL}">{PHONE}</a>, email <a href="mailto:{EMAIL}">{EMAIL}</a> or use the <a href="/contact/">contact form</a>. Read <a href="/reviews/">customer reviews</a> or the <a href="/blog/">blog</a> for answers to common exam questions.</p>
      </div>
      {''.join(groups)}
    </div>
    <p class="f-small">Independent exam prep. Not affiliated with the Mississippi State Board of Contractors or PSI. Prices and packages last synced from Shopify on {UPDATED_TEXT}.</p>
  </div>
</footer>
</body>
</html>
"""


ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": BRAND, "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/assets/icon-512.png", "width": 512, "height": 512}, "image": SITE + "/assets/logo.png", "telephone": PHONE_TEL, "email": EMAIL,
       "parentOrganization": {"@type": "Organization", "name": "1 Exam Prep", "url": "https://1examprep.com/"},
       "sameAs": [v for v in CFG.get("social", {}).values() if v]}
PUB = {"@type": "Organization", "name": BRAND, "url": SITE + "/"}


def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def crumb_html(items):
    parts = [f'<a href="{u}">{e(n)}</a>' for n, u in items[:-1]] + [f'<span aria-current="page">{e(items[-1][0])}</span>']
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(parts) + "</nav>"


def faq_ld(qas):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in qas]}


def faq_html(qas, hid="frequently-asked-questions", title="Frequently asked questions"):
    items = "".join(f'<details class="qa reveal"><summary><h3 id="q-{slugify(q, 50)}">{e(q)}</h3></summary><p>{a}</p></details>' for q, a in qas)
    return f'<section class="sec"><h2 id="{hid}">{title}</h2><div class="faq">{items}</div></section>'


def sources_html(links):
    li = "".join(f'<li><a href="{u}" rel="noopener" target="_blank">{e(n)}</a></li>' for n, u in links)
    return (f'<aside class="sources"><p class="s-h">Sources</p><ul>{li}</ul>'
            f'<p class="updated">Last updated <time datetime="{UPDATED}">{UPDATED_TEXT}</time></p></aside>')


def pic(name, alt, cls="", w=1600, h=900, eager=False, sizes="100vw"):
    """<picture> with every size of assets/img/<name>-<width>.jpg/.webp that exists."""
    import glob
    widths = sorted(int(re.search(r"-(\d+)\.jpg$", f).group(1)) for f in glob.glob(f"assets/img/{name}-*.jpg"))
    srcw = ", ".join(f"/assets/img/{name}-{x}.webp {x}w" for x in widths)
    srcj = ", ".join(f"/assets/img/{name}-{x}.jpg {x}w" for x in widths)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture class="{cls}"><source type="image/webp" srcset="{srcw}" sizes="{sizes}">'
            f'<img src="/assets/img/{name}-{widths[0]}.jpg" srcset="{srcj}" sizes="{sizes}" width="{w}" height="{h}" alt="{e(alt)}" {load}></picture>')


def takeaways(items):
    """Key takeaways box, same markup as the other Pass Your sites."""
    items = [i for i in items if i]
    if not items:
        return ""
    li = "".join(f"<li>{e(i)}</li>" for i in items)
    return (f'<aside class="takeaways reveal" aria-labelledby="key-takeaways"><h2 id="key-takeaways">Key takeaways</h2><ul>{li}</ul>'
            f'<p class="upd">Updated <time datetime="{UPDATED}">{UPDATED_TEXT}</time> · prices checked against the 1 Exam Prep store</p></aside>')


def class_takeaways(c):
    k = CLASSES[c]
    ps = by_class[c]
    n = k["name"]
    out = [f"{len(ps)} Mississippi {n} prep products, from {money(min(p['lo'] for p in ps))} to {money(max(p['hi'] for p in ps))}."]
    x = k.get("exam")
    if x:
        out.append(f"The {n} exam at PSI has {x['q']} questions" + (f" in {x['mins']} minutes" if x.get("mins") else "") + f", open book, with {x['pass_']}% to pass.")
    elif k["group"] == "trade":
        out.append(LOCAL_TRADE + ".")
    elif k["group"] != "business":
        out.append(f"PSI gives the {n} trade exam open book, and MSBOC trade exams need 70% to pass.")
    if k["group"] in ("commercial", "specialty"):
        out.append("A commercial license is needed for jobs over $50,000, including labor and materials.")
    elif k["group"] == "residential":
        out.append("A residential license is needed for new homes over $50,000 and for remodeling or roofing over $10,000.")
    if c != "business-and-law" and k["group"] != "trade":
        out.append("Every applicant also passes the 50-question Law and Business Management exam at 70%.")
    out.append("Every Buy now button goes straight to secure checkout at our fulfillment center, 1 Exam Prep.")
    return out[:5]


def product_takeaways(p, price):
    c = p["cls"]
    n = cls_name(c)
    out = [f"{p['tlabel']} for the Mississippi {n} exam: {price}" + (f", down from {money(p['compare'])}." if p["compare"] > p["hi"] else ".")]
    x = CLASSES[c].get("exam")
    if x:
        out.append(f"The {n} exam has {x['q']} questions and needs {x['pass_']}% to pass, open book at PSI.")
    if not p["ms"]:
        out.append("A national edition that also fits the Mississippi exam.")
    if CLASSES[c]["group"] == "trade":
        out.append(LOCAL_TRADE + ".")
    elif c != "business-and-law":
        out.append("Every Mississippi applicant also takes the 50-question Law and Business Management exam.")
    out.append("Books ship free by USPS Media Mail inside the U.S." if schemakit.ships(p["title"], "") else "Online access arrives by email, with nothing to ship.")
    return out[:5]


def write(path, content):
    fp = os.path.join(OUT, path.strip("/"), "index.html") if not path.endswith((".txt", ".xml", ".md", ".html", ".json")) else os.path.join(OUT, path.strip("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w").write(content)


def exam_line(c):
    x = CLASSES[c].get("exam")
    if not x:
        return (f"PSI gives the {cls_name(c)} trade exam open book; the question count and time limit are in the current "
                f"PSI Mississippi candidate bulletin, and the passing score on MSBOC trade exams is 70%.")
    t = f", with {x['mins']} minutes allowed" if x.get("mins") else ""
    return f"The {cls_name(c)} exam at PSI has {x['q']} questions and needs {x['pass_']}% to pass{t}. You may bring the approved books."


def price_span(p):
    if p["hi"] > p["lo"]:
        return f"{money(p['lo'])} to {money(p['hi'])}"
    return money(p["lo"])


def card(p, show_class=False):
    img = (f'<img src="{e(p["img"])}&width=480" alt="{e(p["alt"])}" width="480" height="480" loading="lazy" decoding="async">'
           if p["img"] else f'<div class="noimg" role="img" aria-label="{e(p["title"])}"><img src="/assets/icon-192.png" alt="Pass Your Mississippi Contractor Exam hard hat icon" width="96" height="96"></div>')
    cmpx = f'<s>{money(p["compare"])}</s> ' if p["compare"] > p["hi"] else ""
    sub = e(cls_name(p["cls"])) if show_class else e(p["tlabel"])
    return (f'<article class="pcard reveal" data-type="{p["tkey"]}"><a href="{p["url"]}">{img}'
            f'<span class="ptag">{sub}</span><h3 id="p-{p["slug"][:60]}">{e(p["title"])}</h3><p class="price">{cmpx}<b>From {money(p["lo"])}</b></p></a></article>')


# ---------------------------------------------------------------- sidebar rail
POPULAR = ["building-construction", "residential-builder", "residential-remodeler", "mechanical", "roofing-sheet-metal-siding", "business-and-law"]


def rail_call():
    return (f'<div class="r-card r-call"><p class="r-h">Need help choosing?</p><p>Tell the 1 Exam Prep team your license and test date, '
            f'and they will match you with the right books.</p><a class="r-phone" href="tel:{PHONE_TEL}">{PHONE}</a>'
            f'<p class="r-small">{EMAIL}</p><a href="/contact/">Send us a message</a></div>')


def rail_class(c, ps, lo, first_hid):
    x = CLASSES[c].get("exam")
    rows = [("Packages", str(len(ps))), ("From", money(lo))]
    if x:
        rows += [("Questions", str(x["q"]))] + ([("Time", f"{x['mins']} min")] if x.get("mins") else []) + [("To pass", f"{x['pass_']}%")]
    else:
        rows += [("Format", "Open book"), ("To pass", "70%")]
    dl = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)
    return (f'<aside class="rail" aria-label="{e(cls_name(c))} quick facts"><div class="rail-in">'
            f'<div class="r-card r-facts"><div class="r-ic">{icon(c)}</div><p class="r-h">{e(cls_name(c))} at a glance</p><dl>{dl}</dl>'
            f'<a class="btn r-btn" href="#{first_hid}">See packages</a></div>'
            f'<div class="r-card"><p class="r-h">Also required</p><p>Every applicant passes the 50-question Law and Business Management exam.</p>'
            f'<a href="/business-and-law/">Law and Business prep</a></div>'
            f'{rail_call()}</div></aside>')


def rail_product(p, buy, price):
    return (f'<aside class="rail" aria-label="Buy {e(p["title"])}"><div class="rail-in">'
            f'<div class="r-card r-buy"><p class="r-h">{e(p["tlabel"])}</p><p class="r-price">{price}</p>'
            f'<a class="btn r-btn" href="{buy}" rel="nofollow">Buy now</a><p class="r-small">Secure checkout at 1 Exam Prep</p></div>'
            f'<div class="r-card"><div class="r-ic">{icon(p["cls"])}</div><p class="r-h">{e(cls_name(p["cls"]))}</p>'
            f'<p>Compare all {len(by_class[p["cls"]])} packages for this license.</p><a href="{cls_url(p["cls"])}">See every package</a></div>'
            f'{rail_call()}</div></aside>')


def rail_popular(label):
    li = "".join(f'<li><a href="{cls_url(c)}"><span class="r-li-ic">{icon(c)}</span>{e(cls_name(c))}</a></li>' for c in POPULAR if by_class.get(c))
    return (f'<aside class="rail" aria-label="{e(label)}"><div class="rail-in">'
            f'<div class="r-card"><p class="r-h">Popular licenses</p><ul class="r-list">{li}</ul>'
            f'<a class="btn r-btn" href="/#find-your-license">All 50 licenses</a></div>'
            f'{rail_call()}</div></aside>')


# ---------------------------------------------------------------- class pages
GROUP_CLASSES = {g: [c for c in CLASSES if CLASSES[c]["group"] == g and by_class.get(c)] for g, *_ in GROUPS}
live_classes = [c for g in GROUP_CLASSES for c in GROUP_CLASSES[g]]


def threshold_text(c):
    g = CLASSES[c]["group"]
    if g == "commercial" or g == "specialty":
        return f"In Mississippi, {COMMERCIAL_RULE}."
    if g == "residential":
        return f"In Mississippi, {RESIDENTIAL_NEW}, and {RESIDENTIAL_REMODEL}."
    if g == "trade":
        return f"{LOCAL_TRADE}. Contractors who bid jobs over the state limits still need an MSBOC license."
    return f"In Mississippi, {COMMERCIAL_RULE}, and {RESIDENTIAL_REMODEL}."


def class_faq(c):
    n = cls_name(c)
    ps = by_class[c]
    cheapest = min(ps, key=lambda p: p["lo"])
    qas = [
        (f"Who needs the Mississippi {n} license?", f"The {n} classification {CLASSES[c]['scope']}. {threshold_text(c)}"),
        (f"How many questions are on the {n} exam?", exam_line(c)),
        ("Is the Mississippi contractor exam open book?", "Yes. MSBOC says every exam is given by PSI and every exam is open book, so tabbed and highlighted books save real time."),
        ("Do I also take the Law and Business Management exam?", LAW + " Reciprocity can waive a trade exam, but it does not waive Law and Business."),
        (f"What is the cheapest way to prepare for {n}?", f"The lowest priced item here is {e(cheapest['title'])} at {money(cheapest['lo'])}. Most candidates pair the books with a course."),
        ("How do I schedule the exam?", "Apply to MSBOC first. When the board confirms you are eligible, PSI emails a notice, and only then can you book a seat."),
        ("How fast do orders ship?", f"Books ship from 1 Exam Prep after checkout and courses open by email. Call {PHONE} with a deadline and the team will tell you the fastest option."),
    ]
    return qas


def class_page(c):
    k = CLASSES[c]
    n = k["name"]
    ps = by_class[c]
    lo = min(p["lo"] for p in ps)
    path = cls_url(c)
    title = f"Mississippi {n} Exam Prep | Books and Courses"
    if len(title) > 60:
        title = f"Mississippi {n} Exam Prep"
    if len(title) > 60:
        title = f"{n} Exam Prep, Mississippi"[:60]
    desc = f"Mississippi {n} exam prep: {len(ps)} packages from {money(lo)}, including highlighted and tabbed books, courses and rentals. Ships from 1 Exam Prep."
    if len(desc) > 160:
        desc = f"{len(ps)} Mississippi {n} exam prep packages from {money(lo)}: tabbed books, courses and rentals."[:160]
    subj = f"Mississippi {n}" if k["group"] == "business" else f"The Mississippi {n} license"
    lead = (f"{subj} {k['scope'].split(';')[0]}. This page lists {len(ps)} prep packages for it, "
            f"starting at {money(lo)}. Pick books, a course or an all-in-one package, then pass the trade exam and the "
            f"50-question Law and Business exam at PSI.")
    lead = lead.replace("This page lists", "We carry")
    if words(lead) > 60:
        lead = (f"{subj} {k['scope'].split(';')[0].split(', which')[0].split(', built')[0]}. We carry {len(ps)} prep packages for it, "
                f"starting at {money(lo)}. Pick books, a course or an all-in-one package, then pass the trade exam and the "
                f"50-question Law and Business exam at PSI.")
    qas = class_faq(c)
    crumb = [("Home", "/"), (n, path)]
    # exam table
    x = k.get("exam")
    rows = [("Who gives the exam", "PSI, for the Mississippi State Board of Contractors"), ("Format", "Open book, approved references only")]
    if x:
        rows.append(("Questions", str(x["q"])))
        if x.get("mins"):
            rows.append(("Time allowed", f"{x['mins']} minutes"))
        rows.append(("Passing score", f"{x['pass_']}%"))
    else:
        rows.append(("Questions and time", "Listed in the current PSI Mississippi bulletin"))
        rows.append(("Passing score", "70% on MSBOC trade exams"))
    rows.append(("Also required", "Law and Business Management, 50 questions, 70%, 2 hours"))
    table = "".join(f"<tr><th scope=\"row\">{e(a)}</th><td>{e(b)}</td></tr>" for a, b in rows)
    # products grouped by type
    types = []
    for p in ps:
        if p["tkey"] not in [t[0] for t in types]:
            types.append((p["tkey"], p["tlabel"]))
    chips = "".join(f'<button type="button" class="chip" data-filter="{t}">{e(l)}</button>' for t, l in types)
    chips = f'<div class="chips" role="group" aria-label="Filter by package type"><button type="button" class="chip on" data-filter="all">All {len(ps)}</button>{chips}</div>' if len(types) > 1 else ""
    # split grid into chunks of <= 9 cards per H2 to keep sections under 400 words
    groups = []
    big = [p for p in ps if p["torder"] <= 5]
    small = [p for p in ps if p["torder"] > 5]
    if len(ps) <= 9 or not big or not small:
        chunks = [ps[i:i + 9] for i in range(0, len(ps), 9)]
        heads = ["Which package should you buy?"] + [f"More {n} packages" for _ in chunks[1:]]
    else:
        chunks = [big[i:i + 9] for i in range(0, len(big), 9)] + [small[i:i + 9] for i in range(0, len(small), 9)]
        nb = len([1 for i in range(0, len(big), 9)])
        heads = ["Which package should you buy?"] + ["More complete packages"] * (nb - 1) + ["Books, courses and add-ons"] + ["More books and add-ons"] * (len(chunks) - nb - 1)
    used_ids = set()
    first_hid = slugify(heads[0], 40)
    grid_html = ""
    for i, (h, ch) in enumerate(zip(heads, chunks)):
        hid = slugify(h, 40)
        while hid in used_ids:
            hid += "-2"
        used_ids.add(hid)
        intro = (f"Packages for {n} run from {money(min(p['lo'] for p in ch))} to {money(max(p['hi'] for p in ch))}. "
                 f"Complete packages save the most hours, while single books suit candidates who already own part of the library.")
        grid_html += f'<section class="sec"><h2 id="{hid}">{e(h)}</h2><p>{intro}</p>{chips if i == 0 else ""}<div class="grid">{"".join(card(p) for p in ch)}</div></section>'
    related = [r for r in GROUP_CLASSES[k["group"]] if r != c][:4] + ["business-and-law"]
    related = [r for r in dict.fromkeys(related) if r != c and by_class.get(r)]
    rel = "".join(f'<li><a href="{cls_url(r)}">{e(cls_name(r))} exam prep</a></li>' for r in related)
    item_list = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"Mississippi {n} exam prep", "url": SITE + path,
                 "description": desc, "dateModified": UPDATED, "publisher": PUB, "isPartOf": {"@id": SITE + "/#website"},
                 "mainEntity": {"@type": "ItemList", "numberOfItems": len(ps), "itemListElement": [
                     {"@type": "ListItem", "position": i + 1, "url": SITE + p["url"], "name": p["title"]} for i, p in enumerate(ps)]}}
    who = (f"The {n} classification {k['scope']}. {threshold_text(c)} Most buyers are {k['who']}. "
           f"The license goes to a business, and its qualifying party is the person who sits for the exams.")
    body = f"""{header()}<main id="main">
<section class="phero phero-class">
  <div class="wrap">
    {crumb_html(crumb)}
    <div class="phero-ic">{icon(c)}</div>
    <div class="eyebrow">{e(dict((g, gn) for g, gn, _ in GROUPS)[k['group']])}</div>
    <h1>Mississippi {e(n)} exam prep</h1>
    <p class="lead">{lead}</p>
    <ul class="facts">
      <li><b data-count="{len(ps)}">{len(ps)}</b> packages</li>
      <li><b>{money(lo)}</b> lowest price</li>
      <li><b data-count="70" data-suffix="%">70%</b> to pass</li>
    </ul>
  </div>
</section>
<div class="wrap cols">
<div class="main-col">
{takeaways(class_takeaways(c))}
<section class="sec"><h2 id="who-needs-it">Who needs the Mississippi {e(n)} license?</h2><p>{who}</p></section>
<section class="sec"><h2 id="what-is-on-the-exam">What is on the {e(n)} exam?</h2><p>{exam_line(c)} MSBOC lets candidates use only the references named in the PSI bulletin, which is why every book package here matches that list.</p>
<table class="facts-table reveal"><caption>{e(n)} exam at a glance</caption><tbody>{table}</tbody></table></section>
{grid_html}
<section class="sec"><h2 id="related-licenses">Related Mississippi licenses</h2><p>Many contractors add a second classification once the first is approved. These pages cover the closest matches and the exam every applicant takes.</p><ul class="links">{rel}<li><a href="/how-to-get-licensed/">How to get a Mississippi contractor license</a></li></ul></section>
{faq_html(qas)}
{sources_html([("Mississippi State Board of Contractors", MSBOC), ("MSBOC testing information", MSBOC_TESTING), ("MSBOC license classifications", MSBOC_CLASSES), ("PSI exams", PSI)])}
</div>
{rail_class(c, ps, lo, first_hid)}
</div>
</main>
{footer()}"""
    ld = [crumbs(crumb), item_list, faq_ld(qas)]
    write(path, head(title, desc, path, ld) + body)


# ---------------------------------------------------------------- product pages
STUDY = {
    "one-package": "Plan on 6 to 8 weeks. Start the application in week 1, read the Law and Business guide in weeks 1 and 2, then take one trade topic a week in the course and finish with 2 full practice exams.",
    "ultimate": "Plan on 6 to 8 weeks inside the 12 months of course access. Work one course module a week with the matching tabbed book open, then return the rental books after the exam.",
    "live": "Attend every live session, then spend 5 to 7 hours a week on self-study between classes. Sit the exam within 2 weeks of the last class while the book layout is fresh.",
    "instructor": "Give the NEC course 2 to 3 sessions a week. Between sessions, work 1 practice exam from the study guide and look up every miss in the tabbed code book.",
    "rental": "Rentals run for a set number of months, so book the exam first and study backward from the date. Aim for 1 book or chapter group a week and 2 timed practice runs.",
    "accelerator": "Send the application paperwork in week 1 so board review runs while you study. Then read 1 book a week and practice finding answers in under 2 minutes.",
    "ht": "Skim every highlighted passage once, then drill lookups. On an open-book exam with roughly 2 to 3 minutes a question, fast tab use matters more than memorizing.",
    "course": "Spend 30 to 60 minutes a day for 4 to 6 weeks. Keep the approved books open while you practice so the course trains your lookups, not just your memory.",
    "practice": "Take 1 timed set every other day for 2 weeks. Review each miss in the book and write the page number on a tab so the answer is 1 flip away.",
    "combo": "Read 1 study guide chapter a day, then take its practice exam with the code book open. Most candidates finish the 12 practice exams in about 4 weeks.",
    "books": "Order early, because the books are the exam. Tab each book on arrival, read the table of contents twice and practice finding answers with a timer.",
    "tabs": "Set aside about 2 hours to place the tabs with the guide. Then run 20 practice lookups so you learn where each colored tab sends you.",
    "service": "Collect your documents in the first week. The application has to be approved before PSI will let you schedule, so filing early protects your exam date.",
    "book": "Read the book once for structure, then use it for lookups during practice exams. Mark the pages you return to most with tabs.",
}


def product_page(p):
    c = p["cls"]
    n = cls_name(c)
    path = p["url"]
    tdesc, includes = TYPE_HELP[p["tkey"]]
    sents = clean_sentences(p["desc"], p["title"], 3)
    short = re.sub(r"\s*[\(\[].*?[\)\]]", "", p["title"]).strip()
    short = short if len(short) < 70 else short[:67].rsplit(" ", 1)[0]
    title = short if len(short) <= 60 else short[:58].rsplit(" ", 1)[0]
    if len(title) < 30:
        title = f"{title} | Mississippi Exam Prep"[:60]
    price = price_span(p)
    desc = f"{short}: {p['tlabel'].lower()} for the Mississippi {n} exam. {price}. Ships from 1 Exam Prep."
    if len(desc) > 160:
        desc = f"{p['tlabel']} for the Mississippi {n} exam, {price}. Ships from 1 Exam Prep."
    if len(desc) < 70:
        desc += " Open-book exam ready."
    scope_note = "" if p["ms"] else " It is a national edition that also fits the Mississippi exam."
    art = "an" if p['tlabel'].lower()[0] in "aeiou" else "a"
    lead = (f"The {short} is {art} {p['tlabel'].lower()} for the Mississippi {n} exam, priced at {price}. "
            f"{tdesc}{scope_note} Buy now opens secure checkout at 1 Exam Prep.")
    while words(lead) > 60:
        lead = lead.rsplit(". ", 1)[0] + "."
    if words(lead) < 40:
        lead += f" Every Mississippi applicant also takes the 50-question Law and Business exam at PSI."
    inc = "".join(f"<li>{e(i)}</li>" for i in includes)
    about = " ".join(e(s) for s in sents) or e(tdesc)
    buy = f"https://1examprep.com/cart/{p['variant']}:1"
    cmp = f'<s>{money(p["compare"])}</s>' if p["compare"] > p["hi"] else ""
    img = (f'<img src="{e(p["img"])}&width=900" alt="{e(p["alt"])}" width="900" height="900" fetchpriority="high">'
           if p["img"] else f'<div class="noimg big" role="img" aria-label="{e(p["title"])}"><img src="/assets/icon-192.png" alt="Pass Your Mississippi Contractor Exam hard hat icon" width="96" height="96"></div>')
    sibs = [s for s in by_class[c] if s is not p][:3]
    sib = "".join(f'<li><a href="{s["url"]}">{e(s["title"])}</a> <span>{money(s["lo"])}</span></li>' for s in sibs)
    qas = [
        (f"Which exam is the {short} for?", f"The {short} is built for the Mississippi {n} exam. {exam_line(c)}"),
        ("Can I bring these books into the PSI exam?", "MSBOC exams are open book, but only the references named in the PSI bulletin are allowed. Highlighting and permanent tabs are generally allowed; loose notes are not."),
        ("Do I still need the Law and Business exam?", LAW),
        ("How much does it cost?", f"The {short} costs {price} before tax and shipping{', down from ' + money(p['compare']) if p['compare'] > p['hi'] else ''}. Upgrades, where offered, are in the option menu at checkout."),
        ("How do I check out?", f"Buy now opens the secure 1 Exam Prep checkout with this item in the cart. Questions before you order go to {PHONE} or {EMAIL}."),
        ("When should I order?", "Order as soon as MSBOC accepts your application. Books take days to arrive, and the tabs and highlights are worth a full week of practice before the exam."),
    ]
    crumb = [("Home", "/"), (n, cls_url(c)), (short, path)]
    offers = {"@type": "Offer", "price": f"{p['lo']:.2f}", "priceCurrency": "USD", "availability": "https://schema.org/InStock",
              "url": SITE + path, "seller": {"@type": "Organization", "name": "1 Exam Prep", "url": "https://1examprep.com"},
              "priceValidUntil": "2027-12-31"}
    if p["hi"] > p["lo"]:
        offers = {"@type": "AggregateOffer", "lowPrice": f"{p['lo']:.2f}", "highPrice": f"{p['hi']:.2f}", "priceCurrency": "USD",
                  "offerCount": 2, "availability": "https://schema.org/InStock", "url": SITE + path,
                  "seller": {"@type": "Organization", "name": "1 Exam Prep", "url": "https://1examprep.com"}}
    cond = schemakit.condition(p["title"], "")
    if cond:
        offers["itemCondition"] = cond
    offers.update(schemakit.delivery_fields(p["title"]))
    prod = {"@context": "https://schema.org", "@type": "Product", "name": p["title"], "url": SITE + path, "sku": str(p["sku"]),
            "description": desc, "brand": {"@type": "Brand", "name": "1 Exam Prep"}, "category": f"Mississippi {n} exam prep",
            "image": [p["img"]] if p["img"] else [SITE + "/assets/img/hero-1600.jpg"], "offers": offers}
    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "url": SITE + path, "name": title, "dateModified": UPDATED, "publisher": PUB}
    body = f"""{header()}<main id="main">
<div class="wrap">
{crumb_html(crumb)}
<div class="pdp">
  <div class="pdp-img reveal">{img}</div>
  <div class="pdp-buy">
    <div class="eyebrow">{e(p['tlabel'])}</div>
    <h1>{e(p['title'])}</h1>
    <p class="lead">{e(lead)}</p>
    <p class="bigprice">{cmp} <b>{price}</b></p>
    <a class="btn" href="{buy}" rel="nofollow">Buy now</a>
    <ul class="assure"><li>Secure checkout at 1 Exam Prep</li><li>Questions? Call <a href="tel:{PHONE_TEL}">{PHONE}</a></li><li>Matched to the PSI reference list</li></ul>
  </div>
</div>
<div class="cols"><div class="main-col">
{takeaways(product_takeaways(p, price))}
<section class="sec"><h2 id="whats-included">What does the {e(short)} include?</h2><p>{about}</p><ul class="ticks">{inc}</ul></section>
<section class="sec"><h2 id="which-exam">Which Mississippi exam is it for?</h2><p>The <a href="{cls_url(c)}">Mississippi {e(n)} license</a> {e(CLASSES[c]['scope'])}. {e(threshold_text(c))} {e(exam_line(c))}</p></section>
<section class="sec"><h2 id="how-to-study">How should you study with it?</h2><p>{e(STUDY[p['tkey']])} Pair it with the <a href="/business-and-law/">Law and Business Management prep</a>, since every applicant sits that 50-question exam too.</p></section>
<section class="sec"><h2 id="other-packages">Other {e(n)} packages</h2><p>Compare these before you buy, or see every option on the <a href="{cls_url(c)}">{e(n)} page</a>.</p><ul class="links">{sib}<li><a href="/how-to-get-licensed/">Steps to a Mississippi license</a></li></ul></section>
{faq_html(qas)}
{sources_html([("MSBOC testing information", MSBOC_TESTING), ("Mississippi State Board of Contractors", MSBOC), ("PSI exams", PSI)])}
</div>{rail_product(p, buy, price)}</div>
</div>
</main>
{footer()}"""
    write(path, head(f"{title}", desc, path, [crumbs(crumb), prod, page_ld, faq_ld(qas)], og_img=p["img"] or "/assets/logo.png") + body)


# ---------------------------------------------------------------- home
HOME_FAQ = [
    ("Who needs a Mississippi contractor license?", "Commercial jobs over $50,000, new homes over $50,000, and residential remodeling or roofing over $10,000 all need an MSBOC license. Fire sprinkler work needs one at $5,000 on public jobs and $10,000 on private jobs."),
    ("Who gives the Mississippi contractor exams?", "PSI gives every MSBOC exam, and MSBOC says all of them are open book."),
    ("What is the Law and Business Management exam?", LAW + " It is built on the Mississippi edition of the NASCLA Contractors Guide to Business, Law and Project Management."),
    ("Can I take the exam before I apply?", "No. You apply to MSBOC first, and PSI emails a scheduling notice only after the board confirms you are eligible."),
    ("Does Mississippi license journeyman electricians or plumbers?", LOCAL_TRADE + ". The study guides here cover those local tests."),
    ("Is the NASCLA exam accepted in Mississippi?", "Yes. MSBOC lists the NASCLA Commercial General Building and electrical exams as options for contractors who work in more than one state. Law and Business is still required."),
    ("What score do I need to pass?", "70% on the Law and Business exam and on the MSBOC trade exams covered here."),
    ("How do I order?", f"Pick your license, choose a package and press Buy now for secure checkout at 1 Exam Prep. Call {PHONE} for help choosing."),
]


def home():
    path = "/"
    total = len(products)
    ncls = len(live_classes)
    title = "Pass Your Mississippi Contractor Exam | MSBOC Prep"
    desc = f"Exam prep for {ncls} Mississippi contractor licenses: tabbed books, courses and Law and Business prep for the open-book PSI exams. {total} packages."
    lead = (f"Passing the Mississippi contractor exam takes 2 tests at PSI: your trade exam and the 50-question Law and Business "
            f"Management exam, both open book with a 70% passing score. Pick your license below for the exact approved books, "
            f"courses and all-in-one packages, {total} in all.")
    groups_html = ""
    for g, gname, gblurb in GROUPS:
        cs = GROUP_CLASSES[g]
        if not cs:
            continue
        cards = ""
        for c in cs:
            ps = by_class[c]
            cards += (f'<a class="ccard reveal" href="{cls_url(c)}" data-name="{e(cls_name(c).lower())}">'
                      f'<span class="c-ic">{icon(c)}</span><span class="c-n">{e(cls_name(c))}</span><span class="c-m">{len(ps)} packages, from {money(min(p["lo"] for p in ps))}</span></a>')
        gid = slugify(gname, 40)
        intro = {"commercial": "Commercial classifications cover jobs over $50,000. Each one has its own PSI trade exam and approved book list.",
                 "residential": "Residential licenses kick in at $50,000 for new homes and $10,000 for remodeling or roofing.",
                 "specialty": "Specialty classifications are narrower commercial licenses. Most carry 1 to 6 approved books.",
                 "trade": "Individual electrician and plumber cards come from your city or county, not the state board. These guides cover those local tests.",
                 "business": "Every applicant passes Law and Business Management. Start here if you have not picked a trade yet."}[g]
        groups_html += f'<section class="sec grp" data-group><h2 id="{gid}">{e(gname)}</h2><p>{intro}</p><div class="cgrid">{cards}</div></section>'
    steps = [
        ("Pick your classification", f"Match your work to 1 of the {ncls} license types on this site and check its dollar limit."),
        ("Form the business", "Register the company with the Mississippi Secretary of State and line up insurance."),
        ("Apply to MSBOC", "Send the application. Commercial applicants include financial statements; the board checks eligibility."),
        ("Schedule at PSI", "PSI emails a notice after approval. Book the trade exam and Law and Business together."),
        ("Pass and get licensed", "Score 70% on each exam with your tabbed books, and the board issues the license."),
    ]
    tl = "".join(f'<li class="step reveal"><span class="s-num">{i + 1}</span><h3 id="step-{i + 1}">{e(a)}</h3><p>{e(b)}</p></li>' for i, (a, b) in enumerate(steps))
    exams = [("Law and Business Management", "50", "120 min", "Every applicant"), ("Building Construction", "80", "180 min", "Commercial"),
             ("NASCLA Commercial General Building", "115", "300 min", "Commercial, multi-state"), ("Residential Builder", "80", "180 min", "Residential"),
             ("Residential Remodeler", "50", "150 min", "Residential"), ("Municipal and Public Works", "60", "120 min", "Commercial")]
    trows = "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in exams)
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "name": BRAND, "url": SITE + "/", "publisher": {"@id": SITE + "/#org"}, "inLanguage": "en-US"}
    org_ld = dict({"@context": "https://schema.org"}, **ORG)
    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "url": SITE + "/", "name": title, "description": desc, "datePublished": CFG["launched"], "dateModified": UPDATED, "publisher": {"@id": SITE + "/#org"}}
    body = f"""{header()}<main id="main">
<section class="hero">
  <div class="hero-media" data-parallax>{pic("hero", "Mississippi contractor in a hard hat and safety vest on a jobsite at sunset, with the State Capitol in Jackson behind him", eager=True)}</div>
  <div class="hero-shade" aria-hidden="true"></div>
  <div class="wrap hero-in">
    <div class="eyebrow">Mississippi State Board of Contractors exams</div>
    <h1><span class="h-line">Pass your Mississippi</span> <span class="h-line">contractor exam</span> <span class="h-line accent">the first time.</span></h1>
    <p class="lead">{lead}</p>
    <form class="finder" action="/" role="search" aria-label="Find your license">
      <label for="finder">Find your license</label>
      <input id="finder" type="search" name="q" placeholder="Try roofing, HVAC or residential builder" autocomplete="off">
      <a class="btn" href="#find-your-license">Browse all</a>
    </form>
  </div>
  <svg class="river" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true"><path d="M0 70 C 240 20, 480 120, 720 70 S 1200 20, 1440 70 V120 H0Z"/></svg>
</section>
<section class="stats wrap" aria-label="Key numbers">
  <div class="stat reveal"><b data-count="{ncls}">{ncls}</b><span>license types covered</span></div>
  <div class="stat reveal"><b data-count="{total}">{total}</b><span>prep packages</span></div>
  <div class="stat reveal"><b data-count="70" data-suffix="%">70%</b><span>score to pass at PSI</span></div>
  <div class="stat reveal"><b data-count="50000" data-prefix="$">$50,000</b><span>commercial license limit</span></div>
</section>
<div class="marquee" aria-hidden="true"><div class="m-track">{''.join(f'<span>{e(cls_name(c))}</span>' for c in live_classes[:24])}</div></div>
<div class="wrap">
{takeaways([f"{total} products across {ncls} Mississippi licenses, from {money(min(p['lo'] for p in products))} to {money(max(p['hi'] for p in products))}.",
            "PSI gives every MSBOC exam, and every exam is open book with a 70% passing score.",
            "Every applicant passes the 50-question Law and Business Management exam plus a trade exam.",
            "A license is needed for commercial jobs and new homes over $50,000, and for remodeling or roofing over $10,000.",
            "Every Buy now button goes straight to secure checkout at our fulfillment center, 1 Exam Prep."])}
<section class="sec intro-sec"><h2 id="find-your-license">Which Mississippi license do you need?</h2><p>MSBOC sorts contractors by classification, and each classification has its own PSI trade exam and approved books. Type a trade in the search box above, or scan the groups below. Every card opens the exam facts, the dollar limit and every package for that license.</p><p class="no-match" hidden>No license matches that search. Try a shorter word, or call {PHONE}.</p></section>
{groups_html}
</div>
<section class="band">
  <div class="wrap band-in">
    <div class="band-txt">
      <h2 id="how-do-you-get-licensed">How do you get a Mississippi contractor license?</h2>
      <p>Getting licensed in Mississippi takes 5 steps and usually 6 to 10 weeks. The board reviews the application before PSI lets you test, so file early and study while you wait. The full walkthrough is on the <a href="/how-to-get-licensed/">licensing guide</a>.</p>
      <ol class="timeline" data-timeline>{tl}</ol>
    </div>
    <div class="band-img reveal"><picture><source media="(min-width: 900px)" type="image/webp" srcset="/assets/img/engineer-portrait-500.webp 500w, /assets/img/engineer-portrait-719.webp 719w" sizes="40vw"><source media="(min-width: 900px)" srcset="/assets/img/engineer-portrait-500.jpg 500w, /assets/img/engineer-portrait-719.jpg 719w" sizes="40vw"><source type="image/webp" srcset="/assets/img/engineer-600.webp 600w, /assets/img/engineer-1199.webp 1199w" sizes="100vw"><img src="/assets/img/engineer-600.jpg" srcset="/assets/img/engineer-600.jpg 600w, /assets/img/engineer-1199.jpg 1199w" sizes="100vw" width="1199" height="1312" alt="Mississippi contractor in a white hard hat and hi-vis vest beside the river at sunset, with the State Capitol dome and a steel truss bridge behind her" loading="lazy" decoding="async"></picture></div>
  </div>
</section>
<div class="wrap">
<section class="sec"><h2 id="exam-lengths">How long are the Mississippi contractor exams?</h2><p>Question counts and time limits differ by classification. The 6 most common exams are below, all open book at PSI with a 70% passing score. Check the bulletin PSI sends with your scheduling notice, since the board can update it.</p>
<div class="tablewrap reveal"><table><caption>Common MSBOC exams at PSI</caption><thead><tr><th scope="col">Exam</th><th scope="col">Questions</th><th scope="col">Time</th><th scope="col">Who takes it</th></tr></thead><tbody>{trows}</tbody></table></div></section>
<section class="sec split"><div><h2 id="why-tabbed-books">Why do tabbed books matter on an open-book exam?</h2><p>An 80-question exam in 180 minutes leaves about 2 minutes a question. Candidates who fail usually know the material but lose time hunting through 10 or more reference books. Highlighted and tabbed sets put the answer 1 flip away, and the online courses drill the same lookups until they are automatic.</p>
<ul class="ticks"><li>Books matched to the PSI reference list</li><li>Highlights on the passages exams use most</li><li>Courses that practice with the books open</li></ul></div>
{pic("plans", "Rolled blueprints, a tape measure, a level and a tablet on a jobsite table", cls="split-img reveal", w=886, h=320, sizes="(min-width: 900px) 45vw, 100vw")}</section>
</div>
<div class="wrap">
{faq_html(HOME_FAQ)}
{sources_html([("Mississippi State Board of Contractors", MSBOC), ("MSBOC testing information", MSBOC_TESTING), ("MSBOC license classifications", MSBOC_CLASSES), ("NASCLA", NASCLA), ("PSI exams", PSI)])}
</div>
</main>
{footer()}"""
    write(path, head(title, desc, path, [org_ld, site_ld, page_ld, faq_ld(HOME_FAQ)], extra='<link rel="preload" as="image" href="/assets/img/hero-1600.webp" type="image/webp">\n') + body)


# ---------------------------------------------------------------- guide page
GUIDE_FAQ = [
    ("How long does it take to get a Mississippi contractor license?", "Most applicants take 6 to 10 weeks from application to license, depending on board review, PSI seat availability and study time."),
    ("Do I need experience to get licensed?", "MSBOC reviews each application against the classification you request. Check the current application on msboc.us for the experience and references it asks for."),
    ("Do residential and commercial applicants take the same business exam?", "Yes. " + LAW),
    ("Does Mississippi have reciprocity?", "MSBOC has reciprocal agreements with several state boards that can waive a trade exam. Law and Business Management is still required."),
    ("Do I need a license for a $40,000 commercial job?", "Not from the state, since the commercial limit is $50,000. Local permits and business licenses still apply."),
    ("Who is the qualifying party?", "The qualifying party is the person who passes the exams on behalf of the licensed business."),
]


def guide():
    path = "/how-to-get-licensed/"
    title = "How to Get a Mississippi Contractor License (2026)"
    desc = "How to get a Mississippi contractor license in 5 steps: dollar limits, MSBOC application, PSI exams, the Law and Business test and timing."
    lead = ("To get a Mississippi contractor license, choose your MSBOC classification, register the business, apply to the "
            "board, then pass 2 open-book exams at PSI: your trade exam and the 50-question Law and Business Management exam, "
            "each at 70%. Most applicants finish in 6 to 10 weeks.")
    crumb = [("Home", "/"), ("How to get licensed", path)]
    secs = [
        ("do-you-need-a-license", "Do you need a state license at all?",
         f"<p>Mississippi sets dollar limits rather than licensing every job. {COMMERCIAL_RULE[0].upper() + COMMERCIAL_RULE[1:]}. For homes, {RESIDENTIAL_NEW}, and {RESIDENTIAL_REMODEL}. Fire sprinkler work is stricter, at $5,000 on public jobs and $10,000 on private ones.</p>"
         "<table><caption>When Mississippi requires a state license</caption><thead><tr><th scope=\"col\">Work</th><th scope=\"col\">License needed above</th></tr></thead><tbody>"
         "<tr><td>Commercial construction</td><td>$50,000</td></tr><tr><td>New residential construction</td><td>$50,000</td></tr>"
         "<tr><td>Residential remodeling or roofing</td><td>$10,000</td></tr><tr><td>Fire sprinklers, public job</td><td>$5,000</td></tr><tr><td>Fire sprinklers, private job</td><td>$10,000</td></tr></tbody></table>"),
        ("step-1-classification", "Step 1: which classification fits your work?",
         f"<p>MSBOC licenses by classification. A general builder usually wants <a href=\"/building-construction/\">Building Construction</a> or the <a href=\"/nascla-commercial-general-building/\">NASCLA Commercial General Building</a> exam, while home builders take <a href=\"/residential-builder/\">Residential Builder</a>. Trades such as <a href=\"/mechanical/\">Mechanical</a>, <a href=\"/roofing-sheet-metal-siding/\">Roofing</a> and <a href=\"/concrete/\">Concrete</a> each have their own exam. This site covers {len(live_classes)} license types with matching prep.</p>"),
        ("step-2-business", "Step 2: set up the business",
         "<p>The license is issued to a business, so form the company first and register it with the Mississippi Secretary of State. Line up general liability and, once you have employees, workers' compensation. A <a href=\"/licensing-and-business-setup/\">business setup service</a> can handle the filing if you would rather not.</p>"),
        ("step-3-apply", "Step 3: apply to the Mississippi State Board of Contractors",
         "<p>Submit the MSBOC application for your classification. Commercial applicants include financial statements with the application, and residential applicants file a shorter form. The board reviews eligibility before anything else happens, so a complete file on day 1 can save weeks.</p>"),
        ("step-4-schedule", "Step 4: when can you schedule at PSI?",
         "<p>After the board confirms you are eligible, PSI emails a scheduling notice. MSBOC is clear that you cannot book a seat before that email arrives. Book the trade exam and Law and Business on the same day if seats allow, and give yourself at least 3 to 4 weeks of study before the date.</p>"),
        ("step-5-pass", "Step 5: how do you pass both exams?",
         f"<p>Every exam is open book, but only the references in the PSI bulletin are allowed. The Law and Business exam has 50 questions in 2 hours, and trade exams run from 40 to 115 questions. Tabbed, highlighted books and timed practice are what move scores past 70%. Start with the <a href=\"/business-and-law/\">Law and Business prep</a>, then your trade page.</p>"
         "<ul class=\"ticks\"><li>Read each book's table of contents twice</li><li>Take at least 2 full timed practice exams</li><li>Aim to find any answer in under 2 minutes</li></ul>"),
        ("common-delays", "What delays a Mississippi license most often?",
         "<p>Most delays come from paperwork, not the exams. Applicants who plan for these 4 problems usually finish inside the 6 to 10 week window.</p>"
         "<ol><li>An incomplete MSBOC application, which stops review until the missing page arrives.</li>"
         "<li>Waiting to book PSI until the week you feel ready, when nearby seats may already be taken.</li>"
         "<li>Bringing a book that is not on the PSI reference list, which the proctor will not allow.</li>"
         "<li>Skipping Law and Business prep, even though its 50 questions decide every application.</li></ol>"),
    ]
    sec_html = "".join(f'<section class="sec"><h2 id="{i}">{e(h)}</h2>{b}</section>' for i, h, b in secs)
    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": SITE + path, "description": desc, "dateModified": UPDATED, "publisher": PUB}
    howto = {"@context": "https://schema.org", "@type": "HowTo", "name": "How to get a Mississippi contractor license", "totalTime": "P10W",
             "step": [{"@type": "HowToStep", "position": i + 1, "name": h, "url": SITE + path + "#" + sid} for i, (sid, h, _) in enumerate(secs[1:])]}
    body = f"""{header()}<main id="main">
<section class="phero"><div class="wrap">{crumb_html(crumb)}<div class="eyebrow">Licensing guide</div><h1>How to get a Mississippi contractor license</h1><p class="lead">{lead}</p></div></section>
<div class="wrap cols"><div class="main-col">
{takeaways(["Mississippi licenses by dollar limit: commercial and new homes over $50,000, remodeling or roofing over $10,000.",
            "Apply to MSBOC first; PSI emails a scheduling notice only after the board approves you.",
            "Pass 2 open-book exams at PSI, your trade exam and the 50-question Law and Business exam, each at 70%.",
            "Most applicants finish in 6 to 10 weeks, and paperwork causes more delays than the exams."])}
{pic("skyline", "Downtown Jackson skyline and the Mississippi State Capitol dome at sunset", cls="wide reveal", w=1036, h=414, sizes="(min-width: 900px) 760px, 100vw")}
{sec_html}
{faq_html(GUIDE_FAQ)}
{sources_html([("MSBOC license applications", MSBOC_LICENSES), ("MSBOC testing information", MSBOC_TESTING), ("MSBOC license classifications", MSBOC_CLASSES), ("Mississippi 811", MS811), ("PSI exams", PSI)])}
</div>{rail_popular("Popular Mississippi licenses")}</div></main>
{footer()}"""
    write(path, head(title, desc, path, [crumbs(crumb), page_ld, howto, faq_ld(GUIDE_FAQ)]) + body)


# ---------------------------------------------------------------- FAQ page
def faq_page():
    path = "/faq/"
    title = "Mississippi Contractor Exam FAQ | MSBOC and PSI"
    desc = "Answers on Mississippi contractor exams: dollar limits, PSI scheduling, open-book rules, the Law and Business exam, NASCLA and local trade cards."
    qas = HOME_FAQ[:4] + GUIDE_FAQ[:3] + [HOME_FAQ[5], HOME_FAQ[4], GUIDE_FAQ[4]]
    lead = ("Mississippi contractors need a state license for commercial jobs over $50,000 and for remodeling over $10,000, "
            "and they test at PSI on 2 open-book exams with a 70% passing score. The answers below cover limits, scheduling, "
            "books and the Law and Business exam.")
    crumb = [("Home", "/"), ("FAQ", path)]
    half = len(qas) // 2
    body = f"""{header()}<main id="main">
<section class="phero"><div class="wrap">{crumb_html(crumb)}<div class="eyebrow">Questions</div><h1>Mississippi contractor exam FAQ</h1><p class="lead">{lead}</p></div></section>
<div class="wrap cols"><div class="main-col">
{takeaways(["Commercial jobs and new homes over $50,000 need an MSBOC license; remodeling or roofing needs one over $10,000.",
            "PSI gives every exam open book, and you need 70% to pass.",
            "Law and Business Management is 50 questions in 2 hours, required of every applicant.",
            "Cities and counties, not the state, license journeyman electricians and plumbers."])}
{faq_html(qas[:half], "licenses-and-limits", "Licenses and dollar limits")}
{faq_html(qas[half:], "exams-and-scheduling", "Exams and scheduling")}
<section class="sec"><h2 id="exam-facts-at-a-glance">What are the key exam numbers?</h2><p>Mississippi exam rules come down to a few numbers. The table collects the ones candidates ask about most, drawn from MSBOC and the PSI bulletin.</p>
<table><caption>Mississippi contractor exam numbers</caption><tbody><tr><th scope="row">Law and Business Management</th><td>50 questions, 2 hours, 70% to pass</td></tr><tr><th scope="row">Building Construction</th><td>80 questions, 180 minutes</td></tr><tr><th scope="row">Residential Builder</th><td>80 questions, 180 minutes</td></tr><tr><th scope="row">NASCLA Commercial General Building</th><td>115 questions, 300 minutes</td></tr><tr><th scope="row">Commercial license limit</th><td>Jobs over $50,000</td></tr><tr><th scope="row">Residential remodel or roofing limit</th><td>Jobs over $10,000</td></tr></tbody></table></section>
<section class="sec"><h2 id="how-to-study-open-book">How should I study for an open-book exam?</h2><p>Open-book exams reward speed with the books more than memory. An 80-question exam in 180 minutes leaves a little over 2 minutes a question, so the goal is to know where every answer lives.</p>
<ol><li>Tab every approved book the day it arrives, using pre-printed tabs if you have them.</li><li>Read each table of contents twice and note which book covers which topic.</li><li>Take at least 2 full timed practice exams with only the approved books open.</li><li>Look up every missed question and mark the page, so the next lookup takes 1 flip.</li></ol></section>
<section class="sec"><h2 id="which-license-to-pick">Which license page should I start with?</h2><p>Most visitors land on 1 of 6 licenses. Each page lists the approved books, the exam length and every package with its price.</p>
<ul class="links"><li><a href="/building-construction/">Building Construction</a> for commercial general contractors</li><li><a href="/residential-builder/">Residential Builder</a> for new homes over $50,000</li><li><a href="/residential-remodeler/">Residential Remodeler</a> for remodels over $10,000</li><li><a href="/mechanical/">Mechanical</a> for HVAC, plumbing and gas piping contractors</li><li><a href="/roofing-sheet-metal-siding/">Roofing, Sheet Metal and Siding</a> for commercial roofers</li><li><a href="/master-electrician-contractor/">Electrical</a> for commercial electrical contractors</li></ul></section>
<section class="sec"><h2 id="still-have-a-question">Still have a question?</h2><p>Call {PHONE} or email <a href="mailto:{EMAIL}">{EMAIL}</a>, and the 1 Exam Prep team will match you with the right books. You can also start from the <a href="/how-to-get-licensed/">licensing guide</a>, the <a href="/business-and-law/">Law and Business page</a> or the <a href="/#find-your-license">full list of licenses</a>.</p></section>
{sources_html([("MSBOC testing information", MSBOC_TESTING), ("Mississippi State Board of Contractors", MSBOC), ("PSI exams", PSI)])}
</div>{rail_popular("Popular Mississippi licenses")}</div></main>
{footer()}"""
    write(path, head(title, desc, path, [crumbs(crumb), faq_ld(qas)]) + body)


# ---------------------------------------------------------------- contact page
FORM_ID = "1jGx4TPpXO5C3XkV5vuq"
CONTACT_FAQ = [
    ("How do I contact 1 Exam Prep about a Mississippi exam?", f"Use the form on this page, call {PHONE} or email {EMAIL}. All 3 reach the same 1 Exam Prep team that ships the orders."),
    ("What should I put in my message?", "Name your license classification, your PSI test date if you have one, and which books you already own. That is enough to recommend the right package."),
    ("Can you tell me which license I need?", "The team can walk you through the classifications. The Mississippi State Board of Contractors makes the final call on any application."),
    ("Can I order by phone?", f"Yes. Call {PHONE} and the team can place the order with you, or send you a link to the right package."),
    ("Where do I ask about an order I already placed?", f"Use the form or email {EMAIL} with your order number, and the team will look it up."),
    ("Does 1 Exam Prep schedule my PSI exam?", "No. MSBOC approves your application and PSI emails the scheduling notice. The team can explain each step, and the application service can file the MSBOC paperwork for you."),
]


def contact_page():
    path = "/contact/"
    title = "Contact Us | Pass Your Mississippi Contractor Exam"
    desc = f"Contact 1 Exam Prep about Mississippi contractor exam prep: send the form, call {PHONE} or email {EMAIL} for help choosing books and courses."
    lead = (f"To reach 1 Exam Prep about a Mississippi contractor exam, send the form on this page, call {PHONE} or email {EMAIL}. "
            "Tell us your license classification and your PSI test date, and the team will point you to the right books, "
            "course or all-in-one package.")
    crumb = [("Home", "/"), ("Contact", path)]
    form = (f'<div class="form-card reveal"><div class="form-embed" data-form-id="{FORM_ID}" data-form-name="passyourmississippicontractorexam.com" data-height="560">'
            f'<p class="form-fallback">The contact form is loading. If it does not appear, call <a href="tel:{PHONE_TEL}">{PHONE}</a> '
            f'or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div></div>')
    page_ld = {"@context": "https://schema.org", "@type": ["WebPage", "ContactPage"], "name": title, "url": SITE + path, "description": desc,
               "dateModified": UPDATED, "publisher": PUB, "mainEntity": {"@type": "Organization", "name": BRAND, "url": SITE + "/",
               "contactPoint": {"@type": "ContactPoint", "contactType": "customer service", "telephone": PHONE_TEL, "email": EMAIL,
                                "areaServed": "US-MS", "availableLanguage": "English"}}}
    body = f"""{header()}<main id="main">
<section class="phero"><div class="wrap">{crumb_html(crumb)}<div class="eyebrow">Contact</div><h1>Contact us</h1><p class="lead">{lead}</p></div></section>
<div class="wrap cols"><div class="main-col">
{takeaways([f"Reach 1 Exam Prep by the form on this page, by phone at {PHONE} or by email at {EMAIL}.",
            "Include your license classification, your PSI test date and the books you already own.",
            f"The same team that ships every order answers, across {len(products)} Mississippi products.",
            "MSBOC decides every application; the team helps with products and the paperwork."])}
<section class="sec"><h2 id="send-a-message">How do I send a message?</h2><p>Fill in the form below and press submit. Your message goes straight to the 1 Exam Prep team, which handles every order for this site. Include your phone number if you would rather get a call back.</p>{form}</section>
<section class="sec"><h2 id="other-ways-to-reach-us">What are the other ways to reach us?</h2><p>Some questions are faster by phone, especially when a test date is close. Use whichever of the 3 options suits you.</p>
<table><caption>Ways to contact 1 Exam Prep</caption><tbody><tr><th scope="row">Phone</th><td><a href="tel:{PHONE_TEL}">{PHONE}</a></td></tr><tr><th scope="row">Email</th><td><a href="mailto:{EMAIL}">{EMAIL}</a></td></tr><tr><th scope="row">Form</th><td>On this page, answered by the same team</td></tr></tbody></table></section>
<section class="sec"><h2 id="what-to-include">What should you include in your message?</h2><p>A few details let the team recommend the right package on the first reply instead of the third. Mississippi has 50 license types on this site, and the approved books differ for each one, so the classification matters most of all.</p>
<ul class="ticks"><li>Your license classification, such as Building Construction or Residential Builder</li><li>Your PSI test date, or the month you hope to test</li><li>Which approved books you already own</li><li>Whether you still need to file the MSBOC application</li></ul></section>
<section class="sec"><h2 id="what-we-help-with">What can the team help with?</h2><p>Most messages fall into 4 groups. The team answers questions about the products and the licensing steps; the Mississippi State Board of Contractors decides every application.</p>
<ol><li>Choosing between books, rentals, courses and the all-in-one packages for your license.</li><li>Orders already placed, including shipping and rental returns.</li><li>The MSBOC application and the <a href="/licensing-and-business-setup/">application service</a>.</li><li>Preparing for the 50-question <a href="/business-and-law/">Law and Business Management exam</a>.</li></ol>
<p>Before you write, the <a href="/how-to-get-licensed/">licensing guide</a> and the <a href="/faq/">FAQ</a> answer the most common questions about dollar limits, PSI scheduling and open-book rules.</p></section>
<section class="sec"><h2 id="who-answers">Who answers your message?</h2><p>1 Exam Prep runs this site and fulfils every order on it, so the people who read the form are the same people who pack the books and open course access. The Mississippi catalog runs from single items at {money(min(p["lo"] for p in products))} to complete rental packages at {money(max(p["hi"] for p in products))}, across {len(products)} products. Because the team sees every package, it can compare a $1,000 book set with a rental or an online course for your exact license and test date. For questions about the law itself, such as whether a job needs a license, the <a href="{MSBOC}" rel="noopener" target="_blank">Mississippi State Board of Contractors</a> has the final word.</p></section>
{faq_html(CONTACT_FAQ)}
{sources_html([("Mississippi State Board of Contractors", MSBOC), ("MSBOC testing information", MSBOC_TESTING), ("PSI exams", PSI)])}
</div>{rail_popular("Popular Mississippi licenses")}</div></main>
{footer()}"""
    write(path, head(title, desc, path, [crumbs(crumb), page_ld, faq_ld(CONTACT_FAQ)]) + body)


def reviews_page():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")); import reviewskit as rk
    c = rk.content(BRAND, "Mississippi contractor exam", PHONE, PHONE_TEL, EMAIL)
    path = rk.PATH
    crumb = [("Home", "/"), ("Reviews", path)]
    secs = "".join(f'<section class="sec"><h2 id="{i}">{h}</h2>{b}</section>\n' for i, h, b in c["sections"])
    body = f"""{header()}<main id="main">
<section class="phero"><div class="wrap">{crumb_html(crumb)}<div class="eyebrow">Reviews</div><h1>{c["h1"]}</h1><p class="lead">{c["lead"]}</p></div></section>
<div class="wrap cols"><div class="main-col">
{takeaways(c["takeaways"])}
{secs}{faq_html(c["faq"])}
{sources_html(c["sources"])}
</div>{rail_popular("Popular Mississippi licenses")}</div></main>
{footer()}"""
    write(path, head(c["title"], c["desc"], path, [crumbs(crumb), rk.page_ld(SITE, c["title"], c["desc"], UPDATED, SITE + "/#org"), faq_ld(c["faq"])]) + body)


# ---------------------------------------------------------------- agent files
def agent_files():
    urls = ["/", "/how-to-get-licensed/", "/faq/", "/contact/", "/reviews/"] + BLOG_URLS + [cls_url(c) for c in live_classes] + [p["url"] for p in products]
    sm = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{UPDATED}</lastmod></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\nUser-agent: Google-Extended\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n\nUser-agent: Bingbot\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    lic = "\n".join(f"- [{cls_name(c)} exam prep]({SITE}{cls_url(c)}): {len(by_class[c])} packages from {money(min(p['lo'] for p in by_class[c]))}" for c in live_classes)
    txt = f"""# {BRAND}

> Exam prep for Mississippi State Board of Contractors (MSBOC) licenses. PSI gives every exam open book. All applicants pass the 50-question Law and Business Management exam (70%, 2 hours) plus a trade exam. Orders are fulfilled by 1 Exam Prep. Phone {PHONE}, email {EMAIL}. Updated {UPDATED}.

## Key pages
- [Blog]({SITE}/blog/)
- [How to get a Mississippi contractor license]({SITE}/how-to-get-licensed/)
- [FAQ]({SITE}/faq/)
- [Contact]({SITE}/contact/)
- [Customer reviews]({SITE}/reviews/)
- [Law and Business Management exam prep]({SITE}/business-and-law/)

## Licenses
{lic}

## Facts
- Commercial license: jobs over $50,000. Residential: new homes over $50,000, remodeling or roofing over $10,000. Fire sprinklers: $5,000 public, $10,000 private.
- Mississippi has no statewide journeyman or master electrician or plumber license; cities and counties issue those.
"""
    write("llms.txt", txt)
    write("agents.md", txt.replace(f"# {BRAND}", f"# {BRAND}: guide for agents") + f"\n## How to buy\nEach product page has a Buy now link to `https://1examprep.com/cart/<variant-id>:1`, which opens Shopify checkout with that item.\n")


def not_found():
    write("404.html", head("Page not found | Pass Your Mississippi Contractor Exam", "That page moved or never existed. Find your Mississippi license exam prep from the home page.", "/404.html", [{"@context": "https://schema.org", "@type": "WebPage", "name": "Page not found"}]).replace('content="index, follow, max-image-preview:large"', 'content="noindex"') +
          f'{header()}<main id="main"><section class="phero"><div class="wrap"><h1>That page is not here</h1><p class="lead">Start from the <a href="/">home page</a> or the <a href="/faq/">FAQ</a>.</p></div></section></main>{footer()}')


if __name__ == "__main__":
    # Remove only what the last build generated (listed in .build-manifest.json), never source files.
    MAN = ".build-manifest.json"
    if os.path.exists(MAN):
        for d in json.load(open(MAN)):
            if os.path.isdir(d):
                shutil.rmtree(d)
            elif os.path.isfile(d):
                os.remove(d)
    home(); guide(); faq_page(); contact_page(); reviews_page()
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")); import blogpages
    BLOG_URLS = blogpages.build(globals())
    agent_files(); not_found()
    for c in live_classes:
        class_page(c)
    for p in products:
        product_page(p)
    if CFG.get("siteUrl"):
        open("CNAME", "w").write(SITE.split("//")[1] + "\n")
    open(".nojekyll", "w").close()
    gen = ["index.html", "404.html", "sitemap.xml", "robots.txt", "llms.txt", "agents.md", "how-to-get-licensed", "faq", "contact", "reviews", "blog"] + live_classes
    json.dump(gen, open(MAN, "w"), indent=0)
    print(f"Built {len(live_classes)} license pages and {len(products)} product pages into the repo root")
