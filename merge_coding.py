"""
Compare the three authors' blind codings with each other (and with the AI coding), then build the final
workbook from the agreed, majority and adjudicated values.

Step 1, compare:
    python merge_coding.py compare
  -> manual_coding/agreement_report.md   Fleiss' kappa across the three coders, Cohen's kappa per pair,
                                         per-field agreement for the charting
  -> manuscript/agreement_table.tex      the same, as the supplement's agreement table
  -> manual_coding/adjudication.xlsx     what needs a decision, one row per record and field:
       'No majority'  all three coders differ: fill 'Final' after discussion (required).
       'Majority'     two of three agree: 'Final' is prefilled with the majority value; change it only if the
                      discussion shows the majority was wrong.
       'Single coder' only one coder charted the record (the others excluded it): 'Final' is prefilled with that
                      coder's value; used only if the record ends up included.
       'AI flags'     the three coders agree but the AI coding differs: 'Final' is prefilled with the coders'
                      value; change it only if the check shows the coders were wrong.
Step 2, after reviewing the sheets and filling every 'No majority' row:
    python merge_coding.py apply
  -> manual_coding/coding_FINAL.xlsx     final values in the coding layout
Then: ./rebuild_results.sh   (or build_dataset.py --coding manual_coding/coding_FINAL.xlsx ...)

Paths can be overridden: --coders, --coding-dir, --ai, --outdir, --texdir (used for test runs).
"""
import argparse
import os
import re
import shutil
from collections import Counter
from itertools import combinations

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

import coding_form as M

BASE = os.path.dirname(os.path.abspath(__file__))
SCREEN = ["Physics education?", "Video-based motion analysis?", "Decision", "Exclusion reason", "Screened on"]
CHART = [c[0] for c in M.CHART_COLS if c[0] != "Charting notes"]
NUMERIC = {"Students (n)", "B: Sample (n)"}
SETLIKE = {"Author countries", "Software (other / additional)", "B: Instrument names"}
KAPPA_FIELDS = ("Decision", "Physics education?", "Video-based motion analysis?")
SHEETS = ("No majority", "Majority", "Single coder", "AI flags")


def header(ws):
    for r in range(1, 6):
        vals = [c.value for c in ws[r]]
        if "ID" in vals:
            return r, {v: i for i, v in enumerate(vals) if v}
    raise SystemExit(f"{ws.title}: no header row")


def read(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {}
    for sheet, fields in (("Screening", SCREEN + ["Notes"]), ("Charting", CHART + ["Charting notes"])):
        ws = wb[sheet]
        hr, col = header(ws)
        ev = [k for k in col if k.startswith("AI evidence") or k == "AI charting evidence"]
        for row in ws.iter_rows(min_row=hr + 1, values_only=True):
            rid = row[col["ID"]]
            if not rid:
                continue
            d = out.setdefault(rid, {})
            for f in fields + ev:
                v = row[col[f]] if f in col else None
                d[f] = "" if v is None else str(v).strip()
    return out


def norm(field, v):
    v = (v or "").strip()
    if field in NUMERIC or field == "Frame rate":
        m = re.search(r"\d+", v)
        return m.group() if m else v.lower()
    if field in SETLIKE:
        return ";".join(sorted(x.strip().lower() for x in re.split(r"[;,]", v) if x.strip()))
    return v


def charted(d):
    return d.get("Decision") == "Include" and d.get("Screened on") == "Full text"


def cohen(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x and y]
    if not pairs:
        return None, None, 0
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return po, ((po - pe) / (1 - pe) if pe < 1 else 1.0), n


def fleiss(rows):
    """One list of labels per subject (same number of raters each) -> (share where all agree, kappa, n)."""
    rows = [r for r in rows if all(r)]
    if not rows:
        return None, None, 0
    n_r, N = len(rows[0]), len(rows)
    cats = sorted({c for r in rows for c in r})
    counts = [Counter(r) for r in rows]
    p_j = [sum(c[k] for c in counts) / (N * n_r) for k in cats]
    P_i = [(sum(v * v for v in c.values()) - n_r) / (n_r * (n_r - 1)) for c in counts]
    P_bar, P_e = sum(P_i) / N, sum(p * p for p in p_j)
    agree = sum(len(set(r)) == 1 for r in rows) / N
    return agree, ((P_bar - P_e) / (1 - P_e) if P_e < 1 else 1.0), N


def majority(vals):
    """{coder: normalised value} -> the value at least two coders share, or None."""
    c = Counter(vals.values())
    v, k = c.most_common(1)[0] if c else (None, 0)
    return v if k >= 2 else None


def load(a):
    coders = {c: read(os.path.join(a.coding_dir, f"coding_{c}.xlsx")) for c in a.coders}
    ai = read(a.ai) if a.ai and os.path.exists(a.ai) else {}
    ids = sorted(set().union(*[set(d) for d in coders.values()]))
    return coders, ai, ids


def row_of(i, sheet, f, raw, names, ai_val, ai_ev, final):
    return [i, sheet, f] + [raw.get(c, "") for c in names] + [ai_val, (ai_ev or "")[:500], final, ""]


def classify(sheets, i, sheet, f, raw, among, names, ai_val, ai_ev):
    """Put one record-field into the right adjudication sheet (or none, when all coders agree with each other and the AI)."""
    v = {c: norm(f, raw.get(c, "")) for c in among}
    if len(set(v.values())) == 1:
        if ai_val and norm(f, ai_val) != next(iter(v.values())):
            sheets["AI flags"].append(row_of(i, sheet, f, raw, names, ai_val, ai_ev, raw[among[0]]))
        return
    m = majority(v)
    if m is not None:
        sheets["Majority"].append(row_of(i, sheet, f, raw, names, ai_val, ai_ev, next(raw[c] for c in among if v[c] == m)))
    else:
        sheets["No majority"].append(row_of(i, sheet, f, raw, names, ai_val, ai_ev, ""))


def compare(a):
    coders, ai, ids = load(a)
    names = list(coders)
    get = lambda c, i, f: coders[c].get(i, {}).get(f, "")
    pairs = list(combinations(names, 2))
    rep = ["# Agreement report", "", f"Records: {len(ids)}. Coders: {', '.join(names)}" + ("; the AI coding is used only for flags." if ai else "."), "",
           "## Screening", "", "| Field | n | All coders agree | Fleiss' kappa | " + " | ".join(f"{x}-{y} kappa" for x, y in pairs) + " |",
           "|---|---|---|---|" + "---|" * len(pairs)]
    tex_rows = []
    for f in KAPPA_FIELDS:
        ag, k, n = fleiss([[get(c, i, f) for c in names] for i in ids])
        pk = [cohen([get(x, i, f) for i in ids], [get(y, i, f) for i in ids])[1] for x, y in pairs]
        if n:
            rep.append(f"| {f} | {n} | {ag:.1%} | {k:.2f} | " + " | ".join(f"{p:.2f}" if p is not None else "-" for p in pk) + " |")
            tex_rows.append((f.replace("?", ""), n, ag, k))
    all_charted = [i for i in ids if all(charted(coders[c].get(i, {})) for c in names)]
    rep += ["", f"## Charting (records that all coders charted: {len(all_charted)})", "", "| Field | n | All coders agree | Fleiss' kappa |", "|---|---|---|---|"]
    tex_rows.append(None)
    for f in CHART:
        rows = [[norm(f, get(c, i, f)) or "(blank)" for c in names] for i in all_charted]
        rows = [r for r in rows if any(x != "(blank)" for x in r)]
        ag, k, n = fleiss(rows)
        if n:
            rep.append(f"| {f} | {n} | {ag:.0%} | {k:.2f} |")
            tex_rows.append((f.replace("B: ", ""), n, ag, k))
    sheets = {s: [] for s in SHEETS}
    for i in ids:
        cods = {c: coders[c].get(i, {}) for c in names}
        x = ai.get(i, {})
        for f in SCREEN:
            ev = x.get("AI evidence: video analysis" if f == "Video-based motion analysis?" else
                       "AI evidence: physics education" if f == "Physics education?" else "", "")
            classify(sheets, i, "Screening", f, {c: cods[c].get(f, "") for c in names}, names, names, x.get(f, ""), ev)
        among = [c for c in names if charted(cods[c])]
        for f in CHART if among else []:
            raw = {c: (cods[c].get(f, "") if c in among else "") for c in names}
            ai_val = x.get(f, "") if charted(x) else ""
            if len(among) == 1:
                if raw[among[0]]:
                    sheets["Single coder"].append(row_of(i, "Charting", f, raw, names, ai_val, x.get("AI charting evidence", ""), raw[among[0]]))
                continue
            classify(sheets, i, "Charting", f, raw, among, names, ai_val, x.get("AI charting evidence", ""))
    os.makedirs(a.outdir, exist_ok=True)
    wb = openpyxl.Workbook()
    hdr = ["ID", "Sheet", "Field"] + names + ["AI", "AI evidence", "Final", "Note"]
    helps = {"No majority": "All coders differ: fill Final after discussion (required).",
             "Majority": "Two of three coders agree: Final is prefilled with the majority value.",
             "Single coder": "Only one coder charted this record: Final is prefilled with that value; used only if the record is included.",
             "AI flags": "The coders agree but the AI coding differs: Final is prefilled with the coders' value."}
    fcol = hdr.index("Final")
    for name in SHEETS:
        ws = wb.create_sheet(name)
        ws.append([helps[name]])
        ws.append(hdr)
        for c in ws[2]:
            c.font = Font(bold=True)
        for r in sheets[name]:
            ws.append(r)
        for row in ws.iter_rows(min_row=3):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
            row[fcol].fill = PatternFill("solid", fgColor="FFF2CC")
        ws.freeze_panes = "A3"
    del wb["Sheet"]
    wb.save(os.path.join(a.outdir, "adjudication.xlsx"))
    rep += ["", "## To resolve", ""] + [f"- {k}: {len(v)} (screening {sum(r[1] == 'Screening' for r in v)}, charting {sum(r[1] == 'Charting' for r in v)})" for k, v in sheets.items()]
    open(os.path.join(a.outdir, "agreement_report.md"), "w").write("\n".join(rep) + "\n")
    tex = [r"\begin{table}[htbp]",
           rf"\caption{{Agreement among the {len(names)} coders before discussion: share of records on which all coders agreed, and Fleiss' $\kappa$. Charting fields: records that all coders included on full text.}}\label{{tab:agreement}}",
           r"\centering\small", r"\begin{tabular}{@{}lrrr@{}}", r"\toprule", r"Field & $n$ & All agree (\%) & Fleiss' $\kappa$ \\", r"\midrule"]
    for t in tex_rows:
        tex.append(r"\addlinespace" if t is None else f"{t[0].replace('&', chr(92) + '&')} & {t[1]} & {round(100 * t[2])} & {t[3]:.2f} \\\\")
    tex += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    os.makedirs(a.texdir, exist_ok=True)
    open(os.path.join(a.texdir, "agreement_table.tex"), "w").write("\n".join(tex) + "\n")
    print("\n".join(rep[-5:]))
    print(f"-> {a.outdir}/agreement_report.md, {a.outdir}/adjudication.xlsx, {a.texdir}/agreement_table.tex")


def apply(a):
    coders, _, ids = load(a)
    names = list(coders)
    adj = openpyxl.load_workbook(os.path.join(a.outdir, "adjudication.xlsx"), read_only=True, data_only=True)
    final, missing = {}, []
    for name in SHEETS:
        rows = list(adj[name].iter_rows(min_row=2, values_only=True))
        fi = list(rows[0]).index("Final")
        for row in rows[1:]:
            if not row or not row[0]:
                continue
            fv = row[fi]
            if fv in (None, "") and name == "No majority":
                missing.append(f"{row[0]} {row[2]}")
            final[(row[0], row[2])] = "" if fv is None else str(fv).strip()
    if missing:
        raise SystemExit(f"{len(missing)} 'No majority' rows still have no Final value, e.g. {missing[:8]}")

    def value(i, f):
        if (i, f) in final:
            return final[(i, f)]
        pool = names if f in SCREEN else [c for c in names if charted(coders[c].get(i, {}))]
        return next((coders[c][i][f] for c in pool if coders[c].get(i, {}).get(f)), "")
    out = os.path.join(a.outdir, "coding_FINAL.xlsx")
    shutil.copy(os.path.join(a.coding_dir, f"coding_{names[0]}.xlsx"), out)
    wb = openpyxl.load_workbook(out)
    for sheet, fields in (("Screening", SCREEN), ("Charting", CHART)):
        ws = wb[sheet]
        hr, col = header(ws)
        for r in range(hr + 1, ws.max_row + 1):
            rid = ws.cell(row=r, column=col["ID"] + 1).value
            if rid:
                for f in fields:
                    ws.cell(row=r, column=col[f] + 1, value=value(rid, f) or None)
    g = wb["Guide"]
    g.insert_rows(1, 2)
    g.cell(row=1, column=1, value=f"FINAL CODING: values on which the coders ({', '.join(names)}) agreed, majority values, and adjudicated disagreements (merge_coding.py apply).")
    wb.save(out)
    print(f"-> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["compare", "apply"])
    ap.add_argument("--coders", nargs="+", default=["TR", "EAN", "EJM"])
    ap.add_argument("--coding-dir", default=os.path.join(BASE, "manual_coding"))
    ap.add_argument("--ai", default=os.path.join(BASE, "ai_coding_sealed", "coding_AI.xlsx"))
    ap.add_argument("--outdir", default=os.path.join(BASE, "manual_coding"))
    ap.add_argument("--texdir", default=os.path.join(BASE, "manuscript"))
    a = ap.parse_args()
    compare(a) if a.step == "compare" else apply(a)
