"""Write manuscript/charting_fields_table.tex (Supplementary Material S2): every screening and
charting field of the coding workbook with its allowed values, taken from make_coding_sheet.py
so the supplement always matches the form the coders used."""
import os
import coding_form as M

OUT = os.path.join(os.environ.get("REVIEW_TEXDIR", "manuscript"), "charting_fields_table.tex")
FREE = {"Software (other / additional)": "Free text: further software named",
        "Author countries": "Free text: countries of all author affiliations",
        "Students (n)": "Number of students who took part, or not reported",
        "Frame rate": "Value with unit (e.g.\\ 240 fps), or not reported",
        "B: Sample (n)": "Total participants analysed",
        "B: Instrument names": "Named instruments (e.g.\\ FCI, TUG-K)",
        "B: Effect size": "Value and type, if reported (e.g.\\ Hake gain)",
        "Notes": "Free text", "Charting notes": "Free text", "Screened on": "Full text; Title/abstract"}
BLOCK = {"code": "Screening", "core": "Core", "A": "Block A", "B": "Block B", "note": "Notes"}


def esc(s):
    return s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_")


rows = []
for name, lst, _, blk in M.SCREEN_COLS + M.CHART_COLS:
    vals = "; ".join(M.LISTS[lst]) if lst else FREE.get(name, "Free text")
    rows.append(f"{BLOCK[blk]} & {esc(name.replace('B: ', ''))} & {esc(vals)} \\\\")
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(rows) + "\n")
print(f"{len(rows)} fields -> {OUT}")
