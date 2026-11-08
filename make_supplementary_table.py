"""
Generate the included-studies longtable for the Supplementary Material
(manuscript/included_studies_table.tex, \\input by supplementary.tex).

One row per included paper (the analysis dataset, see review_stats.py): first
author, year and full title from merged_v4.bib, physics topic and main software
for full-text papers, and the screening pathway.
"""
import re
import unicodedata

import review_stats as S

import os
OUT = os.path.join(os.environ.get("REVIEW_TEXDIR", "manuscript"), "included_studies_table.tex")


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def bib_entries():
    text = open("merged_v4.bib", encoding="utf-8").read()
    out = []
    for e in re.split(r"\n(?=@\w+\s*\{)", "\n" + text):
        if not e.strip().startswith("@"):
            continue
        get = lambda f: (re.search(rf"(?ims)^\s*{f}\s*=\s*\{{(.*?)\}},?\s*$", e) or [None, ""])[1].strip()
        out.append({"doi": get("doi").lower(), "title": get("title"), "author": get("author"),
                    "year": get("year")})
    return out


# WoS prints some titles in capitals; these words keep their case when such a
# title is converted to sentence case
KEEP_CASE = {"tracker": "Tracker", "stem": "STEM", "ict": "ICT", "fci": "FCI", "pbl": "PBL",
             "newton's": "Newton's", "newton’s": "Newton’s", "atwood": "Atwood", "moodle": "Moodle",
             "charly": "Charly", "garcía’s": "García’s", "garcia's": "Garcia's", "geogebra": "GeoGebra",
             "e-book": "e-book"}
# first-author corrections where the database record lists the authors wrongly
AUTHOR_FIX = {"10.1119/5.0059810": "Miyazaki, Makito and Yamazaki, Yosuke and Hasegawa, Yamato"}


def sentence_case(t):
    letters = [c for c in t if c.isalpha()]
    if not letters or sum(c.isupper() for c in letters) < 0.8 * len(letters):
        return t
    words = t.lower().split(" ")
    out = []
    for i, w in enumerate(words):
        w = KEEP_CASE.get(w.strip('".,:;()'), w) if w.strip('".,:;()') in KEEP_CASE else w
        if i == 0 or (out and out[-1].endswith((":", "."))):
            w = w[:1].upper() + w[1:] if not w.startswith('"') else '"' + w[1:2].upper() + w[2:]
        out.append(w)
    return " ".join(out)


def clean_title(t):
    # Scopus appends the original-language title as "; [ ... ]"
    t = re.sub(r";\s*\[[^\]]*\]\s*$", "", t)
    # WoS export artefacts: TeX quotes, braces, a stray trailing "br"
    t = re.sub(r"``|''|\{''\}", "", t).replace("{", "").replace("}", "")
    t = re.sub(r"\s+br$", "", re.sub(r"\s+", " ", t).strip())
    t = sentence_case(t)
    # guard: drop characters the LaTeX build cannot typeset (e.g. Hangul)
    return "".join(c for c in t if ord(c) < 0x2000 or c in "‘’“”–—")


def tex(s):
    s = re.sub(r"[{}]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    for a, b in (("\\", ""), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("~", r"\textasciitilde{}"), ("^", r"\^{}")):
        s = s.replace(a, b)
    return s


def first_author(authors):
    names = [a.strip() for a in re.split(r"\s+and\s+", authors) if a.strip()]
    if not names:
        return ""
    sur = names[0].split(",")[0].strip()
    if len(names) == 1:
        return sur
    if len(names) == 2:
        return f"{sur} and {names[1].split(',')[0].strip()}"
    return f"{sur} et al."


def main():
    bib = {}
    if os.path.exists("merged_v4.bib"):
        import prisma_identification as P
        bib = {e["_key"]: e for e in P.parse_bib("merged_v4.bib")}
    def row(r, status):
        b = bib.get(r["Bib_Key"], {})
        authors = AUTHOR_FIX.get(r["DOI"]) or b.get("author", "")
        inc = status == "Included"
        return (first_author(authors) or r["First_author"], S.year_of(r), clean_title(b.get("title", "") or r["Title"]),
                S.topic(r) if inc else "--", r["Software (main)"] if inc else "--", status)
    key = lambda x: (norm(x[0]), x[1] or 0)
    rows = sorted((row(r, "Included") for r in S.FINAL), key=key) + sorted((row(r, "Not retrieved") for r in S.TA_INC), key=key)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for a, y, t, tp, sw, p in rows:
            sw = tex(sw).replace("/", "/\\allowbreak{}")      # long tool names in a narrow column
            f.write(f"{tex(a)} & {y} & {tex(t)} & {tex(tp)} & {sw} & {p} \\\\\n")
    print(f"{len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
