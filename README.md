# Pass Your Mississippi Contractor Exam (design: River Steel)

Static site for passyourmississippicontractorexam.com, built from Shopify collection 415587981.

    pip install beautifulsoup4 pillow
    python3 build.py               # writes docs/ (GitHub Pages serves main /docs)
    python3 tools/check_pages.py   # grades every page against "What every page and post needs to pass"
    cd docs && python3 -m http.server 8000

- data/products-raw.json: Shopify export (re-pull to refresh prices)
- tools/msclass.py: title rules that sort products into 50 license classes and package types
- tools/mscopy.py: license copy and Mississippi facts (checked 2026-11-19)
- assets/: River Steel CSS, motion JS (reveals, count-ups, parallax, timeline, license finder, package filter), cropped photos
- Publish: commit docs/ and push; Pages serves main /docs (CNAME included).
