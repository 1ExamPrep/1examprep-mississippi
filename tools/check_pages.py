#!/usr/bin/env python3
"""Grade every built page against "What every page and post needs to pass" (Oct 18, 2026).

Usage: python3 tools/check_pages.py [dist] [--verbose]
Prints one line per failing page and a summary. Exit code 1 if any must-have fails.
"""
import json, os, re, sys
from bs4 import BeautifulSoup

DIST = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "."
VERBOSE = "--verbose" in sys.argv
CFG = json.load(open("site-config.json"))
SITE = CFG["siteUrl"].rstrip("/")
PHONE_DIGITS = re.sub(r"\D", "", CFG["phoneTel"])[-10:]
EMAIL = CFG["email"].lower()
BAD_OPEN = re.compile(r"^(in today'?s|in this (article|post|guide)|welcome to|we all know|have you ever|when it comes to|it'?s no secret|in the ever|as the industry evolves)", re.I)
PRONOUN = re.compile(r"^(this|that|these|those|it|they|he|she|such|here|above|below|as (mentioned|noted|discussed|we saw))\b", re.I)
FIG = re.compile(r"(\$\s?\d[\d,]*(\.\d+)?|\b\d+(\.\d+)?\s?%|\b\d[\d,]*(\.\d+)?\b)")
PLACE = re.compile(r"(\{\{.*?\}\}|\[INSERT|\[YOUR|\[TODO\]|\bTODO\b|\bFIXME\b|\bXXX\b|lorem ipsum|your business name|company name here)", re.I)
TARGET = {"product": (300, 180), "collection": (200, 120), "page": (700, 420), "article": (1200, 720)}


def wc(t):
    return len(re.findall(r"[A-Za-z0-9$%][\w$%,.'’-]*", t))


def text_of(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True))


def check(path, html):
    s = BeautifulSoup(html, "html.parser")
    musts, opps = [], []
    head, body = s.head, s.body
    main = s.find("main") or body
    lds = []
    for sc in s.find_all("script", type="application/ld+json"):
        try:
            lds.append(json.loads(sc.string))
        except Exception as ex:
            musts.append(f"JSON-LD does not parse: {ex}")
    types = set()
    for b in lds:
        for x in (b if isinstance(b, list) else [b]):
            t = x.get("@type")
            types.update(t if isinstance(t, list) else [t])
    ptype = "product" if "Product" in types else "collection" if "CollectionPage" in types else "article" if types & {"Article", "BlogPosting", "NewsArticle"} else "page"
    if not lds:
        musts.append("no JSON-LD")
    want = {"product": {"Product"}, "collection": {"CollectionPage", "ItemList"}, "page": {"WebPage", "Article", "Service", "FAQPage"}, "article": {"Article", "BlogPosting", "NewsArticle"}}[ptype]
    if not types & want:
        opps.append(f"schema type {types} does not match {ptype}")
    # title / description / canonical
    title = (head.title.string or "").strip() if head.title else ""
    if not title:
        musts.append("no title")
    elif not 30 <= len(title) <= 60:
        opps.append(f"title {len(title)} chars: {title}")
    md = head.find("meta", attrs={"name": "description"})
    d = md["content"] if md else ""
    if not d:
        musts.append("no meta description")
    elif not 70 <= len(d) <= 160:
        opps.append(f"description {len(d)} chars")
    can = head.find("link", rel="canonical")
    expect = SITE + ("/" + path.strip("/") + "/" if path.strip("/") else "/")
    if not can:
        musts.append("no canonical")
    elif can["href"] != expect:
        opps.append(f"canonical {can['href']} != {expect}")
    if not head.find("meta", property="og:title") or not head.find("meta", property="og:image"):
        opps.append("og:title/og:image missing")
    rob = head.find("meta", attrs={"name": "robots"})
    if rob and "noindex" in rob.get("content", ""):
        musts.append("noindex")
    if not s.html.get("lang"):
        opps.append("no html lang")
    # headings
    h1s = body.find_all("h1")
    if len(h1s) != 1:
        musts.append(f"{len(h1s)} H1 tags")
    heads = main.find_all(re.compile("^h[1-6]$"))
    last = 1
    for h in heads:
        lv = int(h.name[1])
        if lv > last + 1:
            musts.append(f"skipped heading level h{last}->h{lv}: {text_of(h)[:40]}")
            break
        last = lv
    h23 = [h for h in heads if h.name in ("h2", "h3")]
    if h23 and sum(1 for h in h23 if h.get("id")) / len(h23) < 0.7:
        opps.append("ids on <70% of H2/H3")
    if len(heads) >= 2 and sum(1 for h in heads if text_of(h).endswith("?")) < 2:
        opps.append("fewer than 2 question headings")
    # body text
    for bad in main.select("nav, script, style"):
        pass
    body_txt = text_of(main)
    n = wc(body_txt)
    tgt, fail = TARGET[ptype]
    if n < fail:
        musts.append(f"{n} words, fails below {fail} for {ptype}")
    elif n < tgt:
        opps.append(f"{n} words, target {tgt} for {ptype}")
    # opening paragraph: first <p> in main with 8+ words, not inside nav/aside/footer
    first = None
    for p in main.find_all("p"):
        if p.find_parent(["nav", "aside", "footer", "details", "form"]):
            continue
        if wc(text_of(p)) >= 8:
            first = text_of(p)
            break
    if not first:
        musts.append("no opening paragraph")
    else:
        fw = wc(first)
        if BAD_OPEN.search(first):
            musts.append("opening paragraph starts with a warm-up phrase")
        if fw > 90:
            opps.append(f"opening paragraph {fw} words")
        elif not 40 <= fw <= 60:
            opps.append(f"opening paragraph {fw} words (target 40-60)")
    # sections between H2s
    h2s = main.find_all("h2")
    if n > 300 and len(h2s) < 3:
        musts.append(f"only {len(h2s)} H2 sections")
    secs = []
    for h in h2s:
        txt, el = [], h
        while True:
            el = el.find_next()
            if el is None or el.name == "h2" or (el.name == "aside" and "sources" in el.get("class", [])):
                break
            if el.name in ("p", "li", "td", "th", "h3", "summary", "span", "b", "a", "caption") and not el.find(["p", "li", "td", "h3"]):
                if el.name in ("span", "b", "a") and el.find_parent(["p", "li", "td", "h3"]):
                    continue
                txt.append(text_of(el))
        stxt = " ".join(txt)
        secs.append((text_of(h), wc(stxt), stxt))
    thin = [x for x in secs if x[1] < 40]
    long_ = [x for x in secs if x[1] > 400]
    if long_:
        musts.append("sections over 400 words: " + "; ".join(f"{a[:30]} ({b})" for a, b, _ in long_))
    if secs and len(thin) > len(secs) / 2:
        musts.append("more than half the sections under 40 words")
    for h in h2s + main.find_all("h3"):
        nxt = h.find_next(["p", "li"])
        if nxt is not None and PRONOUN.search(text_of(nxt)):
            musts.append(f"section opens with a back-reference: '{text_of(nxt)[:40]}'")
    # figures
    if n >= 200:
        figs = len(FIG.findall(body_txt))
        if figs < n / 100:
            opps.append(f"{figs} figures for {n} words")
    if n > 600 and not re.search(r"key takeaways", body_txt, re.I):
        opps.append("no Key takeaways box on a page over 600 words")
    if not main.find(["ul", "ol", "table"]):
        opps.append("no list or table")
    faqld = any("FAQPage" in str(b.get("@type")) for b in lds if isinstance(b, dict))
    qa = main.select("details.qa")
    if not qa:
        musts.append("no FAQ section")
    elif not 6 <= len(qa) <= 10 and "faq" not in path:
        opps.append(f"FAQ has {len(qa)} questions")
    if qa and not faqld:
        opps.append("FAQ not in FAQPage schema")
    if not (main.find("time") or "dateModified" in html):
        opps.append("no date")
    # links
    hrefs = [a.get("href", "") for a in body.find_all("a")]
    internal = [h for h in hrefs if h.startswith("/") or h.startswith(SITE)]
    outbound = [h for h in hrefs if h.startswith("http") and not h.startswith(SITE) and "1examprep.com" not in h]
    if len(set(internal)) < 3:
        opps.append("fewer than 3 internal links")
    if n > 300 and not outbound:
        opps.append("no outbound citation")
    for h in hrefs:
        if h.strip() in ("", "#") or h.lower().startswith("javascript:"):
            musts.append(f"dead or javascript link: '{h}'")
            break
    for img in body.find_all("img"):
        if not img.get("alt"):
            opps.append(f"image without alt: {img.get('src', '')[:50]}")
    # sentences
    sents = [x for x in re.split(r"(?<=[.!?])\s+", " ".join(text_of(p) for p in main.find_all("p"))) if wc(x) > 2]
    if sents:
        avg = sum(wc(x) for x in sents) / len(sents)
        if avg >= 26:
            opps.append(f"average sentence {avg:.1f} words")
    # pre-publish blockers
    if body.find("script"):
        musts.append("<script> in body")
    if body.find("iframe"):
        musts.append("iframe in body")
    if re.search(r"\son[a-z]+\s*=", str(body)):
        musts.append("inline event handler")
    if PLACE.search(body_txt):
        musts.append(f"placeholder text: {PLACE.search(body_txt).group(0)}")
    if re.search(r"(^|\s)(#{1,3} |\*\*\w)", body_txt):
        musts.append("raw markdown")
    for ph in re.findall(r"\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b", body.get_text(" ")):
        if re.sub(r"\D", "", ph)[-10:] != PHONE_DIGITS:
            musts.append(f"phone not on profile: {ph}")
    for em in set([x.rstrip(".") for x in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", body.get_text(" "))]):
        if em.lower() != EMAIL:
            musts.append(f"email not on profile: {em}")
    return ptype, n, musts, opps


def main():
    pages = []
    for dp, dirs, fs in os.walk(DIST):
        dirs[:] = [x for x in dirs if not x.startswith(".") and x not in ("tools", "data", "brand", "assets", "docs")]
        for f in fs:
            if f == "index.html":
                pages.append(os.path.join(dp, f))
    total_m = total_o = 0
    clean = 0
    from collections import Counter
    oc = Counter()
    for fp in sorted(pages):
        rel = "/" + os.path.relpath(os.path.dirname(fp), DIST).replace(".", "").strip("/")
        t, n, m, o = check(rel, open(fp).read())
        total_m += len(m)
        total_o += len(o)
        for x in o:
            oc[re.sub(r"[\d.]+", "N", x.split(":")[0])[:60]] += 1
        if m or (VERBOSE and o):
            print(f"{rel} [{t}, {n} words]\n  MUST: " + " | ".join(m) + ("\n  opp: " + " | ".join(o) if o else ""))
        if not m and not o:
            clean += 1
    print(f"\n{len(pages)} pages, {clean} with nothing to fix, {total_m} must-have failures, {total_o} opportunities")
    for k, v in oc.most_common(15):
        print(f"  opp x{v}: {k}")
    sys.exit(1 if total_m else 0)


if __name__ == "__main__":
    main()
