"""Sort Mississippi products into license classes and package types by title.

Order matters: the first rule whose keywords all appear in the lowercased title wins.
New products that match nothing land in "code-books-and-courses" and are printed by build.py.
"""
import re

# (slug, keywords that must all appear, alternative keyword sets...)
CLASS_RULES = [
    ("licensing-and-business-setup", [["application service"], ["application processing"], ["corporation or llc"]]),
    ("nascla-electrical-contractor", [["nascla accredited trade examination for electrical"]]),
    ("nascla-residential-electrician", [["nascla residential electric"]]),
    ("nascla-commercial-general-building", [["nascla commercial general building"], ["nascla examination for commercial general building"], ["mississippi nascla", "commercial general"]]),
    ("business-and-law", [["business and law"], ["law and business"], ["business, law and project management"]]),
    ("residential-builder", [["residential builder"]]),
    ("residential-remodeler", [["residential remodeler"]]),
    ("residential-roofer", [["residential roofer"]]),
    ("residential-electrical-contractor", [["residential electrician contractor"]]),
    ("residential-hvac", [["residential hvac"]]),
    ("residential-plumbing", [["residential plumbing"]]),
    ("building-construction", [["building construction"]]),
    ("heavy-construction", [["heavy construction"]]),
    ("highway-construction", [["highway"], ["road and bridge"]]),
    ("municipal", [["municipal"]]),
    ("underground-utilities", [["underground utilities"], ["regulation of excavation"]]),
    ("marine-construction", [["marine construction"]]),
    ("mechanical", [["mechanical contractor"], ["mississippi mechanical"]]),
    ("hvac", [["mississippi hvac"]]),
    ("ductwork", [["ductwork"]]),
    ("plumbing-contractor", [["mississippi plumbing contractor"]]),
    ("process-piping", [["process piping"]]),
    ("refrigeration", [["refrigeration contractor"]]),
    ("boiler", [["boiler"]]),
    ("insulation", [["insulation contractor"]]),
    ("fire-sprinklers", [["fire sprinkler"]]),
    ("fueling-systems", [["fueling systems"]]),
    ("elevators-and-escalators", [["elevators and escalators"]]),
    ("conveyor-systems", [["conveyor"]]),
    ("alarm-systems", [["alarm systems"]]),
    ("communication-systems", [["communication systems"]]),
    ("transmission-and-distribution-lines", [["transmission and distribution"]]),
    ("master-electrician-contractor", [["master electrician contractor"], ["mississippi master electrician - online"]]),
    ("carpentry", [["carpentry"]]),
    ("concrete", [["concrete contractor"]]),
    ("lathing-plastering-stucco", [["lathing"]]),
    ("remodeling", [["remodeling contractor"]]),
    ("roofing-sheet-metal-siding", [["roofing sheet metal"], ["roofing, sheet metal"]]),
    ("structural-steel", [["structural steel"]]),
    ("glass-and-glazing", [["glass glazing"]]),
    ("excavation-and-grading", [["excavation and grading"]]),
    ("irrigation-systems", [["irrigation"]]),
    ("landscaping", [["landscaping"]]),
    ("sign-erection", [["sign erection"]]),
    ("swimming-pools", [["swimming pool"]]),
    ("welding", [["welding contractor"]]),
    ("journeyman-plumber", [["journeyman plumber"]]),
    ("master-electrician", [["master electrician"], ["master unlimited electrical"]]),
    ("journeyman-electrician", [["journeyman electrician"], ["journeyman's electrician"], ["nascla residential electrical"], ["icc g17"]]),
]


def classify(title):
    t = title.lower().replace("–", "-")
    for slug, alts in CLASS_RULES:
        for words in alts:
            if all(w in t for w in words):
                return slug
    return "code-books-and-courses"


# Package types: (key, label, sort order, keyword sets)
TYPE_RULES = [
    ("one-package", "The 1 Package (all-inclusive)", 1, [["the 1 package"]]),
    ("ultimate", "Ultimate rental package", 2, [["ultimate exam prep rental"], ["ultimate exam prep [", "plumber"], ["ultimate exam prep package"], ["ultimate package"]]),
    ("live", "Live virtual + self study", 3, [["live virtual"]]),
    ("instructor", "Study package with instructor-led course", 3, [["instructor led"]]),
    ("rental", "Book and course rental", 4, [["rental"]]),
    ("accelerator", "Books + Application Accelerator", 5, [["application accelerator"]]),
    ("ht", "Highlighted and tabbed book set", 6, [["highlighted & tabbed"], ["highlighted and tabbed"]]),
    ("course", "Online exam prep course", 7, [["online exam prep"], ["online course"], ["test success online"], ["webinar"], ["online course review"]]),
    ("practice", "Online practice questions", 8, [["practice questions"], ["online practice exam"]]),
    ("combo", "Study guide and code book combo", 5, [["combo"], ["super combo"]]),
    ("books", "Exam book package", 6, [["book package"], ["book set"], ["books package"], ["exam prep package"], ["jump start"], ["complete journeyman"], ["book rental"], ["exam prep [2021"]]),
    ("tabs", "Pre-printed tabs", 9, [["tabs"]]),
    ("service", "Licensing service", 5, [["application service"], ["application processing"], ["corporation or llc"]]),
    ("book", "Single book or study guide", 9, [[""]]),
]


def ptype(title):
    t = title.lower().replace("–", "-")
    for key, label, order, alts in TYPE_RULES:
        for words in alts:
            if all(w in t for w in words):
                return key, label, order
    return "book", "Single book or study guide", 9


STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
          "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
          "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Missouri", "Montana",
          "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
          "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
          "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
          "Wisconsin", "Wyoming", "DBPR", "CILB"]


def clean_sentences(desc, title, limit=3):
    """First sentences of a Shopify description that mention no other state, minus the repeated title."""
    if not desc:
        return []
    d = desc.replace("...", "").replace("…", "").strip()
    if d.lower().startswith(title.lower()):
        d = d[len(title):].strip()
    d = re.sub(r"^[A-Z0-9 \-&;,:+()\[\]'’/]{25,}?(?=[A-Z][a-z])", "", d)  # strip shouted title prefix
    parts = re.split(r"(?<=[.!?])\s+", d)
    out = []
    for p in parts:
        p = p.strip()
        if not p or not p[-1:] in ".!?":
            continue  # cut-off sentence
        if any(re.search(r"\b%s\b" % re.escape(s), p) for s in STATES):
            continue
        if len(p.split()) > 45:
            continue
        out.append(p)
        if len(out) >= limit:
            break
    return out
