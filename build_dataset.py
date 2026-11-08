"""
Turn one coding workbook into the analysis dataset that every manuscript number,
table and figure is computed from.

    python build_dataset.py --coding manual_coding/coding_FINAL.xlsx --out final_coding/coded_dataset.csv

--coding is any workbook in the layout built by make_coding_sheet.py: the
adjudicated final workbook, or a single coder's workbook for testing. The
output has one row per screened record (419), with the screening answers, the
charting fields, and bibliographic data from merged_v4.bib: first author, year,
title, venue, DOI, and author countries from the affiliation field. The
countries are used only for papers included on title and abstract, which are
not charted.
"""
import argparse
import csv
import os
import re

import openpyxl

import coding_form as M
try:
    import prisma_identification as P      # only needed to derive data/records.csv from the raw bibliography
except ImportError:
    P = None

BASE = os.path.dirname(os.path.abspath(__file__))
SCREEN = ["Physics education?", "Video-based motion analysis?", "Decision", "Exclusion reason", "Screened on", "Notes"]
CHART = [c[0] for c in M.CHART_COLS]

COUNTRY_FIX = {"usa": "United States", "united states of america": "United States", "us": "United States",
               "u.s.a.": "United States", "uk": "United Kingdom", "england": "United Kingdom",
               "scotland": "United Kingdom", "wales": "United Kingdom", "peoples r china": "China",
               "people's republic of china": "China", "czechia": "Czech Republic", "south korea": "South Korea",
               "republic of korea": "South Korea", "korea": "South Korea", "turkiye": "Turkey", "türkiye": "Turkey",
               "russian federation": "Russia", "viet nam": "Vietnam"}
US_STATES = re.compile(r"^[A-Z]{2}( \d{5})?( USA)?$")


COUNTRIES = set("""Afghanistan;Albania;Algeria;Argentina;Armenia;Australia;Austria;Azerbaijan;Bahrain;Bangladesh;Belarus;Belgium;Bolivia;Bosnia and Herzegovina;Botswana;Brazil;Brunei;Bulgaria;Cameroon;Canada;Chile;China;Colombia;Costa Rica;Croatia;Cuba;Cyprus;Czech Republic;Denmark;Dominican Republic;Ecuador;Egypt;El Salvador;Estonia;Ethiopia;Finland;France;Georgia;Germany;Ghana;Greece;Guatemala;Honduras;Hong Kong;Hungary;Iceland;India;Indonesia;Iran;Iraq;Ireland;Israel;Italy;Jamaica;Japan;Jordan;Kazakhstan;Kenya;Kosovo;Kuwait;Kyrgyzstan;Latvia;Lebanon;Libya;Lithuania;Luxembourg;Macau;Malawi;Malaysia;Malta;Mexico;Moldova;Mongolia;Montenegro;Morocco;Mozambique;Namibia;Nepal;Netherlands;New Zealand;Nicaragua;Nigeria;North Macedonia;Norway;Oman;Pakistan;Palestine;Panama;Paraguay;Peru;Philippines;Poland;Portugal;Puerto Rico;Qatar;Romania;Russia;Rwanda;Saudi Arabia;Senegal;Serbia;Singapore;Slovakia;Slovenia;South Africa;South Korea;Spain;Sri Lanka;Sudan;Sweden;Switzerland;Syria;Taiwan;Tanzania;Thailand;Tunisia;Turkey;Uganda;Ukraine;United Arab Emirates;United Kingdom;United States;Uruguay;Uzbekistan;Venezuela;Vietnam;Yemen;Zambia;Zimbabwe""".split(";"))


def _country(token):
    t = re.sub(r"\b\d{3,}\b", "", token).strip(" .")
    if US_STATES.match(t) or t.endswith(" USA"):
        return "United States"
    t = COUNTRY_FIX.get(t.lower(), t)
    for name in COUNTRIES:
        if t.lower() == name.lower():
            return name
    return None


def countries_from_affiliation(raw):
    """Countries named in each affiliation (Scopus ';'-separated, WoS one per line); only known country names count."""
    out = []
    for part in re.split(r"[;\n]", raw or ""):
        part = re.sub(r"\(Corresponding Author\)", "", part).strip(" .")
        for token in reversed(part.split(",")):      # the country is normally the last token
            name = _country(token)
            if name:
                if name not in out:
                    out.append(name)
                break
    return "; ".join(out)


def header(ws):
    for r in range(1, 4):
        vals = [c.value for c in ws[r]]
        if "ID" in vals:
            return r, {v: i for i, v in enumerate(vals) if v}
    raise SystemExit(f"{ws.title}: no header row with 'ID'")


def read_sheet(ws, wanted):
    hr, col = header(ws)
    missing = [w for w in wanted if w not in col]
    if missing:
        raise SystemExit(f"{ws.title}: columns missing {missing}")
    rows = {}
    for row in ws.iter_rows(min_row=hr + 1, values_only=True):
        rid = row[col["ID"]]
        if rid:
            rows[rid] = {w: ("" if row[col[w]] is None else str(row[col[w]]).strip()) for w in wanted}
    return rows


RECORD_FIELDS = ["ID", "Bib_Key", "First_author", "Year", "Title", "Venue", "DOI", "Countries_bib"]


def load_records():
    """Bibliographic fields of the 419 screened records: data/records.csv (shipped with the public repository),
    or, when it is absent, derived from merged_v4.bib and manual_coding/records_419.csv and written to data/records.csv."""
    path = os.path.join(BASE, "data", "records.csv")
    if os.path.exists(path):
        return list(csv.DictReader(open(path, encoding="utf-8")))
    bib = {e["_key"]: e for e in P.parse_bib(os.path.join(BASE, "merged_v4.bib"))}
    ids = list(csv.DictReader(open(os.path.join(BASE, "manual_coding", "records_419.csv"), encoding="utf-8-sig")))
    out = []
    for r in ids:
        b = bib[r["Bib_Key"]]
        out.append({"ID": r["ID"], "Bib_Key": r["Bib_Key"], "First_author": M.first_author(b.get("author", "")),
                    "Year": (b.get("year") or "")[:4], "Title": M.clean(b.get("title", "")),
                    "Venue": M.clean(b.get("journal") or b.get("booktitle") or ""), "DOI": P.norm_doi(b.get("doi")),
                    "Countries_bib": countries_from_affiliation(b.get("affiliations") or b.get("affiliation") or "")})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RECORD_FIELDS)
        w.writeheader()
        w.writerows(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coding", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    wb = openpyxl.load_workbook(a.coding, read_only=True, data_only=True)
    scr, ch = read_sheet(wb["Screening"], SCREEN), read_sheet(wb["Charting"], CHART)
    recs = load_records()
    out, problems = [], []
    for r in recs:
        rid = r["ID"]
        s = scr.get(rid) or {}
        if not s.get("Decision"):
            problems.append(f"{rid}: no screening decision")
        row = {"ID": rid, "Bib_Key": r["Bib_Key"], "First_author": r["First_author"], "Year": r["Year"],
               "Title": r["Title"], "Venue": r["Venue"], "DOI": r["DOI"],
               "Physics_education": s.get("Physics education?", ""), "Video_analysis": s.get("Video-based motion analysis?", ""),
               "Decision": s.get("Decision", ""), "Exclusion_reason": s.get("Exclusion reason", ""),
               "Screened_on": s.get("Screened on", ""), "Notes": s.get("Notes", "")}
        c = ch.get(rid, {})
        charted = row["Decision"] == "Include" and row["Screened_on"] == "Full text"
        for k in CHART:
            row[k] = c.get(k, "") if charted else ""
        if charted and not row["Physics topic"]:
            problems.append(f"{rid}: included on full text but not charted")
        row["Countries_bib"] = r["Countries_bib"]
        out.append(row)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    inc = [o for o in out if o["Decision"] == "Include"]
    print(f"{a.out}: {len(out)} records, {len(inc)} included "
          f"({sum(o['Screened_on'] == 'Full text' for o in inc)} full text), {len(problems)} problems")
    for p in problems[:20]:
        print("  ", p)


if __name__ == "__main__":
    main()
