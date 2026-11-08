"""
Reproduce the identification stage of the PRISMA flow from the raw search
exports, and check it against merged_v4.bib (Data Integrity Audit V,
2026-10-20).

The original merge script is not in the folder, and the published counts
(212 duplicates, 413 unique) could not be reproduced. This script replaces it:

  1. parse the three exports (Scopus 310, ERIC 146, WoS 169 = 625 records);
  2. link two records when they share a DOI or a normalised title (Scopus
     appends the original-language title as "; [...]", which is stripped);
  3. each connected group of records is one unique record;
  4. a unique record is a book chapter when its DOIs match the book-chapter
     prefixes of Supplementary S4 and it has no journal or proceedings DOI;
  5. every remaining unique record must appear in merged_v4.bib exactly once.

Step 5 found 17 WoS records without a DOI that the original merge had dropped
as if they were duplicates. They were added to merged_v4.bib and screened in
Audit V (audit5_screening_20261020.csv). Run from the V4 root:

    python prisma_identification.py
"""
import os
import re
import unicodedata
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
EXPORTS = {
    "Scopus": "scopus_export_May 19-2026_60ae04f6-ae19-4506-aef0-a9bf56fdf5a7.bib",
    "ERIC": "eric_v4.bib",
    "WoS": "savedrecs.bib",
}
BOOK = re.compile(r"^10\.(1007/978-|4324/|1201/|1093/oso/)")
# DOIs missing from an export but resolved through Crossref (Audit V)
RESOLVED_DOI = {"WOS:000088846500001": "10.4324/9780203763865-4"}   # ICLS 2000, reissued as a book


def parse_bib(path):
    """Minimal brace-matching BibTeX reader: list of {field: value} dicts."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,]*),", txt):
        i, depth = m.end(), 1
        while i < len(txt) and depth:
            depth += {"{": 1, "}": -1}.get(txt[i], 0)
            i += 1
        body = txt[m.end():i - 1]
        fields = {"_key": m.group(2).strip()}
        for fm in re.finditer(r"(\w[\w-]*)\s*=\s*\{", body):
            j, d = fm.end(), 1
            while j < len(body) and d:
                d += {"{": 1, "}": -1}.get(body[j], 0)
                j += 1
            fields.setdefault(fm.group(1).lower(), body[fm.end():j - 1])
        out.append(fields)
    return out


def norm_doi(d):
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", (d or "").strip().lower())


def norm_title(t):
    t = re.sub(r";\s*\[[^\]]*\]\s*$", "", (t or "").strip())
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\\[a-zA-Z]+", " ", t)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t.lower()).split())


def main():
    recs = []
    for src, fn in EXPORTS.items():
        for e in parse_bib(os.path.join(BASE, fn)):
            recs.append({"src": src, "key": e["_key"],
                         "doi": norm_doi(e.get("doi")) or RESOLVED_DOI.get(e["_key"], ""),
                         "nt": norm_title(e.get("title"))})
    n = len(recs)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    seen = {}
    for i, r in enumerate(recs):
        for k in (("doi", r["doi"]) if r["doi"] else None, ("t", r["nt"])):
            if k is None:
                continue
            if k in seen:
                parent[find(i)] = find(seen[k])
            else:
                seen[k] = i
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)

    def is_book(g):
        dois = {recs[i]["doi"] for i in g if recs[i]["doi"]}
        return bool(dois) and all(BOOK.match(d) for d in dois)

    unique = list(groups.values())
    books = [g for g in unique if is_book(g)]
    keep = [g for g in unique if not is_book(g)]
    by_src = Counter(r["src"] for r in recs)
    print(f"identified {n} (Scopus {by_src['Scopus']}, ERIC {by_src['ERIC']}, WoS {by_src['WoS']})")
    print(f"duplicates removed {n - len(unique)} -> unique {len(unique)}")
    print(f"book chapters removed {len(books)} -> records to screen {len(keep)}")
    se = {find(i) for i, r in enumerate(recs) if r["src"] != "WoS"}
    print(f"(Scopus+ERIC alone: {by_src['Scopus'] + by_src['ERIC']} -> {len(se)} unique)")

    merged = parse_bib(os.path.join(BASE, "merged_v4.bib"))
    m_doi = Counter(norm_doi(m.get("doi")) for m in merged if m.get("doi"))
    m_nt = Counter(norm_title(m.get("title")) for m in merged)
    missing, multiple = [], []
    for g in keep:
        hits = set()
        for i in g:
            for m in merged:
                if (recs[i]["doi"] and norm_doi(m.get("doi")) == recs[i]["doi"]) or \
                        norm_title(m.get("title")) == recs[i]["nt"]:
                    hits.add(m["_key"] + "|" + m.get("title", "")[:40])
        if not hits:
            missing.append(g)
        elif len(hits) > 1:
            multiple.append(hits)
    print(f"merged_v4.bib: {len(merged)} entries; unique records missing from it: {len(missing)}; "
          f"represented more than once: {len(multiple)}")
    for g in missing:
        r = recs[g[0]]
        print("   missing:", r["src"], r["key"], r["nt"][:80])
    for h in multiple:
        print("   multiple:", sorted(h))
    dup_doi = [d for d, c in m_doi.items() if c > 1]
    dup_t = [t for t, c in m_nt.items() if c > 1]
    print(f"duplicate DOIs inside merged_v4.bib: {len(dup_doi)}; duplicate titles: {len(dup_t)}")


if __name__ == "__main__":
    main()
