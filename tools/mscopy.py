"""License class copy and the Mississippi facts behind it.

Facts checked November 19, 2026 against msboc.us (testing page: PSI runs every exam, all exams
open book, Law and Business Management required of all applicants) and against published summaries
of the PSI Mississippi contractor bulletin dated April 23, 2026 for question counts and times.
Re-check the PSI bulletin before changing any number here.
"""

UPDATED = "2026-11-19"
UPDATED_TEXT = "November 19, 2026"

MSBOC = "https://www.msboc.us/"
MSBOC_TESTING = "https://www.msboc.us/general-info/testing/"
MSBOC_CLASSES = "https://www.msboc.us/classifications/"
MSBOC_LICENSES = "https://www.msboc.us/contractors/licenses/"
PSI = "https://www.psiexams.com/"
NASCLA = "https://www.nascla.org/"
MS811 = "https://www.ms811.org/"

COMMERCIAL_RULE = ("a commercial certificate of responsibility from the Mississippi State Board of Contractors "
                   "is needed for commercial jobs over $50,000, including labor and materials")
RESIDENTIAL_NEW = "a residential license is needed to build new homes valued over $50,000"
RESIDENTIAL_REMODEL = "a residential license is needed for remodeling or roofing work over $10,000"
LOCAL_TRADE = ("Mississippi has no statewide journeyman or master license, so individual electricians and plumbers "
               "test with the city or county that issues the card")

LAW = ("Every applicant also passes the Mississippi Law and Business Management exam: 50 questions, "
       "a 70% passing score and 2 hours, taken open book at PSI.")

# group keys
GROUPS = [
    ("commercial", "Commercial classifications", "Major commercial licenses for jobs over $50,000."),
    ("residential", "Residential licenses", "Builder, remodeler, roofer and residential trade licenses."),
    ("specialty", "Specialty trades", "Narrow commercial classifications with their own trade exam."),
    ("trade", "Electricians and plumbers", "Study guides and code books for local journeyman and master tests."),
    ("business", "Business, law and licensing", "The Law and Business exam, the NASCLA guide and application help."),
]

# slug: name, group, short, scope sentence, exam dict or None, extra facts
CLASSES = {
    "building-construction": dict(name="Building Construction", group="commercial",
        scope="covers commercial buildings of any size, along with the concrete, masonry, carpentry, roofing and steel work that goes into them",
        exam=dict(q=80, mins=180, pass_=70), who="general contractors who build offices, stores, schools, churches and multi-family structures"),
    "nascla-commercial-general-building": dict(name="NASCLA Commercial General Building", group="commercial",
        scope="uses the NASCLA Accredited Examination for Commercial General Building Contractors, which PSI gives in Mississippi and several other states accept",
        exam=dict(q=115, mins=300, pass_=70), who="commercial builders who plan to work in more than one state"),
    "heavy-construction": dict(name="Heavy Construction", group="commercial",
        scope="covers bridges, dams, industrial plants, large site work and the heavy civil work around them",
        exam=None, who="civil and industrial contractors"),
    "highway-construction": dict(name="Highway, Street and Bridge Construction", group="commercial",
        scope="covers asphalt and concrete paving, bridges, traffic control and work under the Mississippi road and bridge specifications",
        exam=dict(q=60, mins=None, pass_=70), who="road builders and paving contractors bidding public highway work"),
    "municipal": dict(name="Municipal and Public Works", group="commercial",
        scope="covers water, sewer and storm drainage, streets and other public utility construction for towns and counties",
        exam=dict(q=60, mins=120, pass_=70), who="utility and public works contractors"),
    "underground-utilities": dict(name="Underground Utilities", group="commercial",
        scope="covers pipe, conduit and cable installed below grade, plus excavation near existing utility lines under the state excavation law",
        exam=None, who="pipeline, water line and directional boring contractors"),
    "marine-construction": dict(name="Marine Construction", group="commercial",
        scope="covers docks, piers, bulkheads, seawalls and dredging along the Gulf Coast and inland waterways",
        exam=None, who="contractors who work on the water from Biloxi to the river towns"),
    "mechanical": dict(name="Mechanical", group="commercial",
        scope="is the broad mechanical classification for HVAC, refrigeration, plumbing, gas piping, ductwork and fire sprinkler systems",
        exam=None, who="mechanical contractors who self-perform several trades"),
    "hvac": dict(name="HVAC", group="commercial",
        scope="covers heating, ventilation and air conditioning systems on commercial jobs",
        exam=None, who="commercial HVAC contractors"),
    "plumbing-contractor": dict(name="Plumbing", group="commercial",
        scope="covers commercial plumbing systems, fixtures, water distribution and drainage",
        exam=None, who="commercial plumbing contractors"),
    "master-electrician-contractor": dict(name="Electrical (Master Electrician)", group="commercial",
        scope="is the state electrical contractor classification tested on the National Electrical Code and electrical safety",
        exam=None, who="electrical contractors bidding commercial work"),
    "nascla-electrical-contractor": dict(name="NASCLA Electrical Contractor", group="commercial",
        scope="uses the NASCLA Accredited Trade Examination for Electrical Contractors, which MSBOC lists as an option for contractors working in more than one state",
        exam=None, who="electrical contractors licensed or planning to license in several states"),
    "structural-steel": dict(name="Structural Steel", group="commercial",
        scope="covers the erection of structural steel, joists, decking and related connections",
        exam=None, who="steel erectors and ironwork contractors"),
    "concrete": dict(name="Concrete", group="commercial",
        scope="covers foundations, slabs, formwork, reinforcing and concrete cutting on commercial jobs",
        exam=dict(q=50, mins=120, pass_=70), who="concrete and foundation contractors"),
    "carpentry": dict(name="Carpentry", group="commercial",
        scope="covers framing, finish carpentry, trusses, formwork and cabinetry on commercial jobs",
        exam=None, who="framing and finish carpentry contractors"),
    "remodeling": dict(name="Remodeling (Commercial)", group="commercial",
        scope="covers renovation and repair of existing commercial buildings",
        exam=dict(q=60, mins=135, pass_=70), who="contractors who renovate offices, retail space and churches"),
    "roofing-sheet-metal-siding": dict(name="Roofing, Sheet Metal and Siding", group="commercial",
        scope="covers commercial roofing systems, flashing, sheet metal and siding",
        exam=dict(q=60, mins=120, pass_=70), who="commercial roofing contractors"),
    "lathing-plastering-stucco": dict(name="Lathing, Plastering and Stucco", group="specialty",
        scope="covers lath, plaster, stucco and exterior insulation and finish systems",
        exam=None, who="plaster and stucco contractors"),
    "residential-builder": dict(name="Residential Builder", group="residential",
        scope="covers new home construction; " + RESIDENTIAL_NEW,
        exam=dict(q=80, mins=180, pass_=70), who="home builders in every county from DeSoto to Harrison"),
    "residential-remodeler": dict(name="Residential Remodeler", group="residential",
        scope="covers additions, repairs and renovation of existing homes; " + RESIDENTIAL_REMODEL,
        exam=dict(q=50, mins=150, pass_=70), who="remodelers and home improvement contractors"),
    "residential-roofer": dict(name="Residential Roofer", group="residential",
        scope="covers roofing on houses; " + RESIDENTIAL_REMODEL,
        exam=None, who="residential roofers, including storm-repair crews on the coast"),
    "residential-electrical-contractor": dict(name="Residential Electrical", group="residential",
        scope="covers electrical work in homes under the state residential license",
        exam=None, who="residential electrical contractors"),
    "nascla-residential-electrician": dict(name="NASCLA Residential Electrical", group="residential",
        scope="uses the NASCLA accredited residential electrical exam, given by PSI for Mississippi",
        exam=None, who="residential electrical contractors who want a multi-state exam"),
    "residential-hvac": dict(name="Residential HVAC", group="residential",
        scope="covers heating and air conditioning in homes under the state residential license",
        exam=None, who="residential HVAC contractors"),
    "residential-plumbing": dict(name="Residential Plumbing", group="residential",
        scope="covers plumbing in homes under the state residential license",
        exam=dict(q=80, mins=240, pass_=70), who="residential plumbing contractors"),
    "ductwork": dict(name="Ductwork for Heating, AC and Ventilation", group="specialty",
        scope="covers sheet metal and flexible duct systems for heating and cooling", exam=None, who="duct fabricators and installers"),
    "process-piping": dict(name="Process Piping", group="specialty",
        scope="covers industrial process piping systems in plants and refineries", exam=None, who="industrial piping contractors"),
    "refrigeration": dict(name="Refrigeration", group="specialty",
        scope="covers commercial refrigeration systems, walk-in coolers and ice equipment", exam=None, who="refrigeration contractors"),
    "boiler": dict(name="Boiler Installation and Repair", group="specialty",
        scope="covers boilers, steam and hydronic heating systems", exam=None, who="boiler contractors"),
    "insulation": dict(name="Insulation", group="specialty",
        scope="covers mechanical pipe and duct insulation", exam=None, who="mechanical insulation contractors"),
    "fire-sprinklers": dict(name="Fire Sprinklers", group="specialty",
        scope="covers fire sprinkler systems; a license is needed on public jobs over $5,000 and private jobs over $10,000",
        exam=None, who="fire protection contractors"),
    "fueling-systems": dict(name="Fueling Systems", group="specialty",
        scope="covers fuel dispensing systems, tanks and piping", exam=None, who="petroleum equipment contractors"),
    "elevators-and-escalators": dict(name="Elevators and Escalators", group="specialty",
        scope="covers elevators, escalators and conveying equipment", exam=dict(q=60, mins=120, pass_=70), who="elevator contractors"),
    "conveyor-systems": dict(name="Conveyor Systems", group="specialty",
        scope="covers material handling conveyors in plants and warehouses", exam=None, who="conveyor installers"),
    "alarm-systems": dict(name="Alarm Systems and Equipment", group="specialty",
        scope="covers fire alarm, intrusion and low-voltage alarm systems", exam=None, who="alarm and security contractors"),
    "communication-systems": dict(name="Communication Systems", group="specialty",
        scope="covers voice, data and low-voltage communication cabling", exam=None, who="low-voltage and telecom contractors"),
    "transmission-and-distribution-lines": dict(name="Transmission and Distribution Lines", group="specialty",
        scope="covers overhead and underground power lines and substations", exam=None, who="line construction contractors"),
    "glass-and-glazing": dict(name="Glass, Glazing, Windows and Skylights", group="specialty",
        scope="covers storefronts, curtain wall, windows and skylights", exam=None, who="glazing contractors"),
    "excavation-and-grading": dict(name="Excavation and Grading", group="specialty",
        scope="covers earthwork, grading and site preparation", exam=None, who="dirt and site work contractors"),
    "irrigation-systems": dict(name="Irrigation Systems", group="specialty",
        scope="covers lawn and landscape irrigation design and installation", exam=None, who="irrigation contractors"),
    "landscaping": dict(name="Landscaping", group="specialty",
        scope="covers planting, grading, drainage and hardscape work", exam=dict(q=40, mins=120, pass_=70), who="landscape contractors"),
    "sign-erection": dict(name="Sign Erection", group="specialty",
        scope="covers the erection of signs and sign structures", exam=None, who="sign contractors"),
    "swimming-pools": dict(name="Swimming Pools", group="specialty",
        scope="covers the construction of swimming pools and their equipment", exam=None, who="pool builders"),
    "welding": dict(name="Welding", group="specialty",
        scope="covers structural and pipe welding as a contracting classification", exam=None, who="welding contractors"),
    "journeyman-electrician": dict(name="Journeyman Electrician", group="trade",
        scope="is a local license; " + LOCAL_TRADE,
        exam=None, who="electricians testing for a city or county journeyman card"),
    "master-electrician": dict(name="Master Electrician", group="trade",
        scope="is a local license; " + LOCAL_TRADE,
        exam=None, who="electricians testing for a city or county master card"),
    "journeyman-plumber": dict(name="Journeyman Plumber", group="trade",
        scope="is a local license; " + LOCAL_TRADE,
        exam=None, who="plumbers testing for a city or county journeyman card"),
    "business-and-law": dict(name="Law and Business Management", group="business",
        scope="is the exam every Mississippi applicant takes, commercial or residential, built on the Mississippi edition of the NASCLA Contractors Guide to Business, Law and Project Management",
        exam=dict(q=50, mins=120, pass_=70), who="every qualifying party, whatever the trade"),
    "licensing-and-business-setup": dict(name="License Application and Business Setup", group="business",
        scope="is help with the MSBOC application, the business entity filing and the paperwork that comes before the exam",
        exam=None, who="contractors who want the application done right the first time"),
    "code-books-and-courses": dict(name="Code Books and Courses", group="business",
        scope="collects code reviews and safety courses that support several Mississippi trade exams",
        exam=None, who="candidates who want extra review on the IBC, IPC, NEC or OSHA 1926"),
}

TYPE_HELP = {
    "one-package": ("Everything in one order: the highlighted and tabbed books, the online course, the Law and Business prep, "
                    "the application service and business setup.", ["Highlighted and tabbed exam books", "Online exam prep course",
                    "Law and Business Management prep", "MSBOC application service", "Business entity setup"]),
    "ultimate": ("Rental books that arrive highlighted and tabbed, one year of online course access and the application service.",
                 ["Highlighted and tabbed rental books", "12 months of online course access", "MSBOC application service"]),
    "live": ("Live virtual classes with an instructor plus self-study between sessions.",
             ["Live virtual instruction", "Self-study course access", "Practice on the approved references"]),
    "instructor": ("Study guides, the code book and an instructor-led NEC course in one package.",
                   ["Study guides and practice exams", "Code book with tabs", "Instructor-led NEC course"]),
    "rental": ("The approved reference books on loan for the months you study, so you skip buying the whole library.",
               ["The listed reference books, rented", "Return shipping after the exam", "Optional course access on some versions"]),
    "accelerator": ("The exam books plus the Application Accelerator, which organizes the MSBOC application.",
                    ["The listed exam books", "Application Accelerator support", "Highlighting on the Highlighted Edition"]),
    "ht": ("Your own copy of every listed book, highlighted and tabbed so you can find answers fast in an open-book exam.",
           ["Every listed reference book", "Exam-focused highlighting", "Permanent pre-printed tabs"]),
    "course": ("Self-paced online exam prep you can work through on a phone or laptop.",
               ["Online lessons by exam topic", "Practice questions with answers", "Book-navigation drills"]),
    "practice": ("Online practice questions that mirror the exam topics.", ["Timed practice tests", "Answer explanations", "Score tracking"]),
    "combo": ("A study guide paired with the code book, tabs or flash cards.", ["Study guide with practice exams", "Code book", "Tabs or flash cards, by version"]),
    "books": ("The reference books listed for the exam, new, in one shipment.", ["The listed exam reference books", "Shipped together", "Upgrade options in the variant menu"]),
    "tabs": ("Pre-printed adhesive tabs cut to the approved books.", ["Labeled tabs for each book", "Placement guide", "Sized for open-book testing"]),
    "service": ("Help preparing and filing your MSBOC license application or business entity.", ["Application review", "Document checklist", "Filing support"]),
    "book": ("A single reference book or study guide.", ["One book or guide", "Practice exams where listed", "Ships from 1 Exam Prep"]),
}
