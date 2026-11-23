"""Blog pages for the Pass Your sites built with the single-file build.py (Florida, Mississippi).

build.py calls build(globals()) after the other pages. Posts are content/posts/*.md, read by tools/blogkit.py
(front matter: title, date, updated, author, excerpt, metaTitle, metaDescription, tags, takeaways, status).
Writes /blog/ and /blog/<slug>/ with BlogPosting (Person author), BreadcrumbList and FAQPage schema, the Key takeaways
box and an FAQ rendered as details.qa so tools/check_pages.py counts it. Returns the list of blog URLs for the sitemap.
"""
import html, os, re

import blogkit

BLOG_FAQ = [
    ("Who writes the posts on this blog?", "Max Ace writes the posts. Each one answers the questions people search most about getting licensed in this state, and every answer is checked against the licensing board and exam vendor pages linked in its Sources list."),
    ("How often are new posts added?", "New posts go up when the board changes a rule, a fee or an exam, and when readers keep asking a question the site does not answer yet. Each post shows the date it was last updated."),
    ("Are the blog answers legal advice?", "No. The posts explain the licensing rules in plain words so you can plan, but the board has the final say. Always confirm details with the board before you apply or pay a fee."),
    ("Where do the facts in each post come from?", "From the licensing board, the state statutes and rules, and the exam vendor's candidate information. Each post lists its sources at the end so you can check them yourself."),
    ("Can I ask a question that is not covered?", "Yes. Use the contact page, call (877) 775-9400 or email sales@1examprep.com. Questions that come up often become new posts."),
    ("Does the blog sell anything?", "The posts are free to read. When a post mentions books or prep courses, it links to the exam prep pages on this site, where you can compare packages and prices."),
]


def _qa(body, slugify):
    """Turn the post's <details><summary>Q</summary> blocks into the site's details.qa markup with an h3 question."""
    def rep(m):
        q = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        return '<details class="qa"%s><summary><h3 id="q-%s">%s</h3></summary>' % (m.group(1) or "", slugify(q, 50), html.escape(q, quote=False))
    return re.sub(r"<details( open)?>\s*<summary>(.*?)</summary>", rep, body, flags=re.S)


def _nice(d):
    import datetime
    t = datetime.date.fromisoformat(d)
    return t.strftime("%B ") + str(t.day) + t.strftime(", %Y")


def build(ns):
    SITE, e, write, head, header, footer = ns["SITE"], ns["e"], ns["write"], ns["head"], ns["header"], ns["footer"]
    crumbs, crumb_html, faq_ld, faq_html, takeaways, slugify = ns["crumbs"], ns["crumb_html"], ns["faq_ld"], ns["faq_html"], ns["takeaways"], ns["slugify"]
    PUB, ORG, BRAND = ns["PUB"], ns["ORG"], ns["BRAND"]
    rail = ns["rail_popular"]
    state = ns.get("STATE_NAME", "")
    posts = [q for q in blogkit.load_posts(os.path.join("content", "posts"), SITE) if q.get("kind", "blog") != "page"]
    urls = []
    if not posts:
        return urls
    logo = ORG.get("logo")
    pub = dict(PUB, **({"logo": logo} if logo else {}))
    for q in posts:
        path = "/blog/%s/" % q["slug"]
        title = q["meta_title"] or q["title"]
        desc = q["meta_description"] or q["excerpt"][:158]
        crumb = [("Home", "/"), ("Blog", "/blog/"), (q["title"], path)]
        body = _qa(q["html"], slugify)
        minutes = max(1, round(q["words"] / 220))
        post_ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": q["title"][:110], "description": desc,
                   "datePublished": q["date"], "dateModified": q["updated"], "inLanguage": "en-US",
                   "author": {"@type": "Person", "name": q["author"] or "Max Ace"}, "publisher": pub,
                   "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + path}, "url": SITE + path,
                   "image": q["image"] or SITE + "/assets/logo.png", "wordCount": q["words"], "keywords": ", ".join(q["tags"])}
        lds = [crumbs(crumb), post_ld] + ([faq_ld(q["faq"])] if q["faq"] else [])
        meta = ('<div class="post-meta"><span>By %s</span> &middot; <time datetime="%s">Updated %s</time> &middot; <span>%d min read</span></div>'
                % (e(q["author"] or "Max Ace"), q["updated"], _nice(q["updated"]), minutes))
        page = f"""{header()}<main id="main">
<section class="phero"><div class="wrap">{crumb_html(crumb)}<div class="eyebrow">Blog</div><h1>{e(q["title"])}</h1>{meta}</div></section>
<div class="wrap cols"><div class="main-col"><article class="post">
{takeaways(q["takeaways"])}
<div class="prose">{body}</div>
</article></div>{rail("Popular licenses")}</div></main>
{footer()}"""
        write(path, head(title, desc, path, lds) + page)
        urls.append(path)
    # index
    path = "/blog/"
    title = ("%s Contractor License Blog | Exam Answers" % state).strip()
    desc = ("Plain answers about the %s contractor license and exam: costs, hours, open-book rules, scheduling and renewal, written by Max Ace." % state).replace("  ", " ")
    lead = ("This blog answers the questions people search most about getting a %s contractor license and passing the exam. "
            "Every post is written by Max Ace, kept short and plain, and checked against the board and exam vendor pages it lists as sources." % state).replace("  ", " ")
    crumb = [("Home", "/"), ("Blog", path)]
    cards = "".join(
        f'<li><a href="/blog/{q["slug"]}/"><b>{e(q["title"])}</b></a><br>{e(q["excerpt"])} <time datetime="{q["updated"]}">Updated {_nice(q["updated"])}</time></li>' for q in posts)
    secs = (f'<section class="sec"><h2 id="latest-posts">What are the latest posts?</h2><p>The newest posts are listed first. Each one opens with a short answer, then covers the details in plain sections you can skim.</p><ul class="ticks">{cards}</ul></section>'
            '<section class="sec"><h2 id="how-to-use">How should you use these posts?</h2><p>Start with the question closest to where you are. If you are still deciding whether you need a license, read the first sections of a post. If you are booking an exam, jump to the sections on scheduling, books and passing. Each post ends with a Sources list, so you can open the board page and confirm a rule before you act on it.</p></section>'
            '<section class="sec"><h2 id="what-is-next">What comes after reading a post?</h2><p>Most readers move on to the <a href="/how-to-get-licensed/">licensing guide</a>, which lays out every step in order, or the <a href="/faq/">FAQ</a> for quick answers. When you know your license, the exam prep pages show the books, courses and practice tests made for that exam, with prices and what each package includes.</p></section>')
    body = f"""{header()}<main id="main">
<section class="phero"><div class="wrap">{crumb_html(crumb)}<div class="eyebrow">Blog</div><h1>{e(state + " contractor license blog")}</h1><p class="lead">{e(lead)}</p></div></section>
<div class="wrap cols"><div class="main-col">
{takeaways(["Posts answer the questions people search most about the %s license and exam." % state, "Every post is written by Max Ace and lists the official sources it used.", "Each post shows the date it was last updated, so you can tell if it is current.", "Use the licensing guide and the FAQ next, then pick your exam prep."])}
{secs}
{faq_html(BLOG_FAQ)}
{ns["sources_html"](list(ns.get("SRC_CORE", [])))}
</div>{rail("Popular licenses")}</div></main>
{footer()}"""
    page_ld = {"@context": "https://schema.org", "@type": ["WebPage", "CollectionPage"], "name": title, "url": SITE + path, "description": desc, "publisher": PUB,
               "hasPart": [{"@type": "BlogPosting", "headline": q["title"], "url": SITE + "/blog/%s/" % q["slug"]} for q in posts]}
    write(path, head(title, desc, path, [crumbs(crumb), page_ld, faq_ld(BLOG_FAQ)]) + body)
    return [path] + urls
