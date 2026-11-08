"""
Compare the two authors' blind codings with each other and with the AI coding,
then build the final workbook from the agreed and adjudicated values.

Step 1, compare:
    python merge_coding.py compare
  -> manual_coding/agreement_report.md   agreement and Cohen's kappa (screening), per-field agreement (charting)
  -> manual_coding/adjudication.xlsx     what needs a decision:
       'Disagreements': the two authors differ. Fill 'Final' after discussion (the AI value is shown as a third opinion).
       'AI flags':      the authors agree but the AI differs. 'Final' is prefilled with the authors' value; change it only
                        if the check shows the authors were wrong.
Step 2, after filling 'Final':
    python merge_coding.py apply
  -> manual_coding/coding_FINAL.xlsx     agreed values plus adjudicated values, in the coding layout
Then: python build_dataset.py --coding manual_coding/coding_FINAL.xlsx --out final_coding/coded_dataset.csv

Paths can be overridden: --tr, --ean, --ai, --outdir (used for test runs on synthetic data).
"""
import argparse
import os
import re
import shutil
from collections import Counter

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

import coding_form as M

BASE = os.path.dirname(os.path.abspath(__file__))
SCREEN = ["Physics education?", "Video-based motion analysis?", "Decision", "Exclusion reason", "Screened on"]
CHART = [c[0] for c in M.CHART_COLS if c[0] != "Charting notes"]
NUMERIC = {"Students (n)", "B: Sample (n)"}
SETLIKE = {"Author countries", "Software (other / additional)", "B: Instrument names"}


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
    if field in NUMERIC:
        m = re.search(r"\d+", v)
        return m.group() if m else v.lower()
    if field in SETLIKE:
        return ";".join(sorted(x.strip().lower() for x in re.split(r"[;,]", v) if x.strip()))
    if field == "Frame rate":
        m = re.search(r"\d+", v)
        return m.group() if m else v.lower()
    return v


def kappa(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x and y]
    if not pairs:
        return None, None, 0
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0, n


def charted(d):
    return d.get("Decision") == "Include" and d.get("Screened on") == "Full text"


def compare(a):
    tr, ean, ai = read(a.tr), read(a.ean), read(a.ai)
    ids = sorted(set(tr) | set(ean))
    rep = ["# Agreement report", "", f"Records: {len(ids)}. Coders: TR = `{os.path.basename(a.tr)}`, EAN = `{os.path.basename(a.ean)}`, "
           f"AI = `{os.path.basename(a.ai)}`.", "", "## Screening", "",
           "| Field | Pair | n | Agreement | Cohen's kappa |", "|---|---|---|---|---|"]
    for f in ("Decision", "Physics education?", "Video-based motion analysis?"):
        for name, x, y in (("TR-EAN", tr, ean), ("TR-AI", tr, ai), ("EAN-AI", ean, ai)):
            po, k, n = kappa([x.get(i, {}).get(f, "") for i in ids], [y.get(i, {}).get(f, "") for i in ids])
            rep.append(f"| {f} | {name} | {n} | {po:.1%} | {k:.2f} |" if n else f"| {f} | {name} | 0 | - | - |")
    rep += ["", "## Charting (records both authors charted)", "", "| Field | n | TR-EAN agreement | TR-AI | EAN-AI |", "|---|---|---|---|---|"]
    both = [i for i in ids if charted(tr.get(i, {})) and charted(ean.get(i, {}))]
    for f in CHART:
        def ag(x, y, pool):
            p = [(norm(f, x[i].get(f)), norm(f, y[i].get(f))) for i in pool if i in x and i in y]
            p = [q for q in p if q[0] or q[1]]
            return (sum(u == v for u, v in p) / len(p), len(p)) if p else (None, 0)
        a1, n1 = ag(tr, ean, both)
        a2, _ = ag(tr, ai, [i for i in both if charted(ai.get(i, {}))])
        a3, _ = ag(ean, ai, [i for i in both if charted(ai.get(i, {}))])
        fmt = lambda v: "-" if v is None else f"{v:.0%}"
        rep.append(f"| {f} | {n1} | {fmt(a1)} | {fmt(a2)} | {fmt(a3)} |")
    dis, flags = [], []
    for i in ids:
        t, e, x = tr.get(i, {}), ean.get(i, {}), ai.get(i, {})
        fields = SCREEN + (CHART if (charted(t) or charted(e)) else [])
        for f in fields:
            tv, ev, av = t.get(f, ""), e.get(f, ""), x.get(f, "")
            sheet = "Screening" if f in SCREEN else "Charting"
            evid = x.get("AI evidence: video analysis" if f == "Video-based motion analysis?" else
                         "AI evidence: physics education" if f == "Physics education?" else "AI charting evidence", "")
            if norm(f, tv) != norm(f, ev):
                dis.append([i, sheet, f, tv, ev, av, evid[:500], "", ""])
            elif norm(f, av) != norm(f, tv) and (f in SCREEN or charted(x)):
                flags.append([i, sheet, f, tv, ev, av, evid[:500], tv, ""])
    os.makedirs(a.outdir, exist_ok=True)
    wb = openpyxl.Workbook()
    hdr = ["ID", "Sheet", "Field", "TR", "EAN", "AI", "AI evidence", "Final", "Note"]
    for name, rows, help_ in (("Disagreements", dis, "The authors differ: fill Final after discussion."),
                              ("AI flags", flags, "The authors agree, the AI differs: Final is prefilled with the authors' value.")):
        ws = wb.create_sheet(name)
        ws.append([help_])
        ws.append(hdr)
        for c in ws[2]:
            c.font = Font(bold=True)
        for r in rows:
            ws.append(r)
        for col, w in zip("ABCDEFGHI", (7, 10, 26, 22, 22, 22, 60, 22, 30)):
            ws.column_dimensions[col].width = w
        for row in ws.iter_rows(min_row=3):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
            row[7].fill = PatternFill("solid", fgColor="FFF2CC")
        ws.freeze_panes = "A3"
    del wb["Sheet"]
    wb.save(os.path.join(a.outdir, "adjudication.xlsx"))
    rep += ["", "## To resolve", "", f"- Disagreements between the authors: {len(dis)} "
            f"(screening {sum(r[1] == 'Screening' for r in dis)}, charting {sum(r[1] == 'Charting' for r in dis)})",
            f"- AI flags (authors agree, AI differs): {len(flags)}"]
    open(os.path.join(a.outdir, "agreement_report.md"), "w").write("\n".join(rep) + "\n")
    tex = [r"\begin{table}[htbp]", r"\caption{Agreement between the two coders before discussion. Charting fields: records both coders included on full text.}\label{tab:agreement}",
           r"\centering\small", r"\begin{tabular}{@{}lrrr@{}}", r"\toprule", r"Field & $n$ & Agreement (\%) & Cohen's $\kappa$ \\", r"\midrule"]
    for f in ("Decision", "Physics education?", "Video-based motion analysis?"):
        po, k, nn = kappa([tr.get(i, {}).get(f, "") for i in ids], [ean.get(i, {}).get(f, "") for i in ids])
        if nn:
            tex.append(f"{f.replace('?', '')} & {nn} & {round(100 * po)} & {k:.2f} \\\\")
    tex.append(r"\addlinespace")
    for f in CHART:
        p_ = [(norm(f, tr[i].get(f)), norm(f, ean[i].get(f))) for i in both]
        p_ = [q for q in p_ if q[0] or q[1]]
        if p_:
            po, k, nn = kappa([u for u, _ in p_], [v for _, v in p_])
            tex.append(f"{f.replace('B: ', '').replace('&', chr(92) + '&')} & {nn} & {round(100 * po)} & {k:.2f} \\\\")
    tex += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    open(os.path.join(a.texdir, "agreement_table.tex"), "w").write("\n".join(tex) + "\n")
    print("\n".join(rep[-3:]))
    print(f"-> {a.outdir}/agreement_report.md, {a.outdir}/adjudication.xlsx")


def apply(a):
    tr, ean = read(a.tr), read(a.ean)
    adj = openpyxl.load_workbook(os.path.join(a.outdir, "adjudication.xlsx"), read_only=True, data_only=True)
    final, missing = {}, []
    for name in ("Disagreements", "AI flags"):
        for row in adj[name].iter_rows(min_row=3, values_only=True):
            if not row or not row[0]:
                continue
            rid, sheet, f, fv = row[0], row[1], row[2], row[7]
            if fv in (None, "") and name == "Disagreements":
                missing.append(f"{rid} {f}")
            final[(rid, f)] = "" if fv is None else str(fv).strip()
    if missing:
        raise SystemExit(f"{len(missing)} disagreements still have no Final value, e.g. {missing[:8]}")
    out = os.path.join(a.outdir, "coding_FINAL.xlsx")
    shutil.copy(a.tr, out)              # same layout; values overwritten below
    wb = openpyxl.load_workbook(out)
    for sheet, fields in (("Screening", SCREEN), ("Charting", CHART)):
        ws = wb[sheet]
        hr, col = header(ws)
        for r in range(hr + 1, ws.max_row + 1):
            rid = ws.cell(row=r, column=col["ID"] + 1).value
            if not rid:
                continue
            for f in fields:
                v = final.get((rid, f), tr.get(rid, {}).get(f, ""))
                ws.cell(row=r, column=col[f] + 1, value=v or None)
    g = wb["Guide"]
    g.insert_rows(1, 2)
    g.cell(row=1, column=1, value="FINAL CODING: agreed values of both authors plus adjudicated disagreements (merge_coding.py apply).")
    wb.save(out)
    print(f"-> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["compare", "apply"])
    ap.add_argument("--tr", default=os.path.join(BASE, "manual_coding", "coding_TR.xlsx"))
    ap.add_argument("--ean", default=os.path.join(BASE, "manual_coding", "coding_EAN.xlsx"))
    ap.add_argument("--ai", default=os.path.join(BASE, "ai_coding_sealed", "coding_AI.xlsx"))
    ap.add_argument("--outdir", default=os.path.join(BASE, "manual_coding"))
    ap.add_argument("--texdir", default=os.path.join(BASE, "manuscript"))
    a = ap.parse_args()
    compare(a) if a.step == "compare" else apply(a)
