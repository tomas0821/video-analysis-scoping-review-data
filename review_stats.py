"""
Single source of truth for every number reported in the manuscript.

Shared by generate_figures.py, manuscript_numbers.py, make_results_tables.py and
make_supplementary_table.py, so the text, the tables and the figures cannot
drift apart. Input: the analysis dataset written by build_dataset.py from the
final (adjudicated) coding workbook. The path can be overridden for test
builds:

    REVIEW_DATASET=path/to/coded_dataset.csv python manuscript_numbers.py

The charting categories are the coding-guide lists (make_coding_sheet.py), so
little bucketing is needed. The functions below keep the names the figure and
table scripts use.
"""
import csv
import os
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
DATASET = os.environ.get("REVIEW_DATASET", os.path.join(BASE, "final_coding", "coded_dataset.csv"))
SEARCH_YEAR = 2026            # searches run 19-20 May 2026: 2026 is a partial year

if not os.path.exists(DATASET):
    raise SystemExit(f"Analysis dataset not found: {DATASET}\n"
                     "Build it first: python build_dataset.py --coding <workbook> --out <csv>")
with open(DATASET, encoding="utf-8") as _f:
    ROWS = list(csv.DictReader(_f))
for _r in ROWS:   # names used by the older figure code
    _r["Filename"] = _r["ID"]
    _r["Journal"] = _r["Venue"]
    _r["Video_Analysis_Software"] = _r.get("Software (main)", "")
    _r["Research_Design"] = _r.get("Paper type", "")

SCREENED = len(ROWS)                                                   # 419
FT_ALL = [r for r in ROWS if r["Screened_on"] == "Full text"]          # screened on full text
# Included = included on full text (authors' decision 2026-11-08). Records whose full text could not be
# retrieved are "reports not retrieved" in the PRISMA flow, whatever their title/abstract screening said.
CLEAN = [r for r in ROWS if r["Decision"] == "Include" and r["Screened_on"] == "Full text"]   # included and charted
FINAL = CLEAN                                                                                # all included
NOT_RETRIEVED = [r for r in ROWS if r["Screened_on"] != "Full text"]
TA_INC = [r for r in NOT_RETRIEVED if r["Decision"] == "Include"]       # not retrieved, but eligible on title/abstract
EMPIRICAL = [r for r in CLEAN if r["Paper type"] == "Empirical study with students"]


def is_ft(row):
    return row["Screened_on"] == "Full text"


def year_of(row):
    try:
        return int(row["Year"])
    except (TypeError, ValueError):
        return None


# ── topic ───────────────────────────────────────────────────────────────────
TOPIC_ORDER = ["Mechanics", "Oscillations & Waves", "Electromagnetism", "Optics",
               "Thermodynamics", "Fluids", "Modern & Nuclear Physics", "Astronomy", "Other"]
SUBTOPIC_ORDER = ["Kinematics & Free Fall", "Projectile Motion", "Dynamics & Forces",
                  "Circular & Rotational Motion", "Collisions & Momentum",
                  "Energy Conservation", "Friction & Drag", "Gravitation & Orbital Motion",
                  "Other / Mixed Mechanics"]


def topic(row):
    return row["Physics topic"]


def subtopic(row):
    return row["Mechanics subtopic"]


# ── software / paper type / hardware / setting / level ───────────────────────
def bucket_sw(raw):
    r = (raw or "").strip()
    if r in ("Tracker", "Logger Pro", "COACH", "Viana"):
        return r
    if r in ("", "Not stated"):
        return "Not specified"
    return "Other"


DESIGN_ORDER = ["Activity description", "Implementation report", "Empirical study",
                "Accuracy or methods study", "Other"]


def bucket_design(d):
    return {"Empirical study with students": "Empirical study"}.get(d, d or "Other")


def bucket_hw(h):
    return "Not specified" if h in ("", "Not stated") else h


def bucket_setting(s):
    return {"Lab": "Laboratory", "Not stated": "Not specified", "": "Not specified"}.get(s, s)


def level_flags(row):
    y = lambda k: row.get(k) == "Yes"
    return {"Middle school": y("Middle school"), "High school": y("High school"),
            "Undergraduate (any)": y("Undergraduate intro") or y("Undergraduate advanced"),
            "Undergraduate introductory": y("Undergraduate intro"),
            "Teachers / teacher education": y("Teacher education"), "Not specified": y("Level not stated")}


# ── venues ───────────────────────────────────────────────────────────────────
VENUE_FIX = [
    (r"^(the )?physics teacher$", "The Physics Teacher"),
    (r"^revista brasileira de ensino de f[ií]sica$", "Revista Brasileira de Ensino de Física"),
    (r"^revista mexicana de f[ií]sica e$", "Revista Mexicana de Física E"),
    (r"nuovo cimento", "Il Nuovo Cimento C"),
    (r"^proceedings of science", "Proceedings of Science (PoS)"),
    (r"^imsci", "IMSCI (Multi-Conference on Society, Cybernetics and Informatics)"),
    (r"latin american conference on learning technologies", "LACLO"),
    (r"sefi", "SEFI Annual Conference"),
    (r"asee annual conference", "ASEE Annual Conference"),
    (r"^2022 elektro", "ELEKTRO 2022"),
]


def venue(raw):
    import re
    v = (raw or "").strip()
    vl = v.lower()
    for pat, rep in VENUE_FIX:
        if re.search(pat, vl):
            return rep
    if vl in ("", "not mentioned"):
        return "Not mentioned"
    letters = [c for c in v if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) > 0.6 * len(letters):     # WoS prints venues in capitals
        small = {"of", "and", "the", "in", "for", "on", "de", "da", "do", "e", "y"}
        v = " ".join(w.lower() if i and w.lower() in small else (w if any(ch.isdigit() for ch in w) else w.capitalize())
                     for i, w in enumerate(v.split()))
    return re.sub(r"\bOF\b", "of", v)


# ── countries ────────────────────────────────────────────────────────────────
NAME_MAP = {"usa": "United States", "united states of america": "United States", "us": "United States",
            "uk": "United Kingdom", "czechia": "Czech Republic", "korea": "South Korea",
            "republic of korea": "South Korea", "türkiye": "Turkey", "turkiye": "Turkey"}


def _split(raw):
    out = []
    for part in (raw or "").replace(",", ";").split(";"):
        p = part.strip()
        if not p or p.lower() in ("not stated", "not mentioned", "unclear"):
            continue
        out.append(NAME_MAP.get(p.lower(), p))
    return out


def countries_of(row):
    """Charted author countries for full-text papers; bibliographic affiliations for papers included on title/abstract."""
    raw = row.get("Author countries", "") if is_ft(row) else row.get("Countries_bib", "")
    return sorted(set(_split(raw)))


AFRICA = {"South Africa", "Nigeria", "Kenya", "Ghana", "Ethiopia", "Egypt", "Morocco",
          "Tunisia", "Algeria", "Tanzania", "Uganda", "Cameroon", "Zimbabwe", "Zambia",
          "Senegal", "Rwanda", "Botswana", "Namibia", "Mozambique", "Sudan", "Malawi"}
SOUTH_ASIA = {"India", "Pakistan", "Sri Lanka", "Bangladesh", "Nepal"}
MIDDLE_EAST = {"Turkey", "Israel", "Iran", "Saudi Arabia", "Jordan", "Lebanon", "Iraq",
               "United Arab Emirates", "Qatar", "Oman", "Kuwait"}
LATAM = {"Brazil", "Mexico", "Argentina", "Chile", "Colombia", "Costa Rica", "Ecuador",
         "Peru", "Uruguay", "Venezuela", "Bolivia", "Paraguay", "Cuba"}


def pct(k, n):
    return round(100 * k / n) if n else 0


def counter(rows, fn):
    return Counter(fn(r) for r in rows)
