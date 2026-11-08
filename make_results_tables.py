"""
Write the Results tables as complete LaTeX table environments, \\input by main.tex:
  table_summary.tex       Table 1: characteristics of the included papers
  table_practice.tex      Table 2: how the activities were run and measured (block A)
  table_evidence_map.tex  Table 3: evidence map of the empirical studies (block B)
Output folder: manuscript/ (override with REVIEW_TEXDIR for test builds).
"""
import os
from collections import Counter

import review_stats as S

OUT = os.environ.get("REVIEW_TEXDIR", os.path.join(S.BASE, "manuscript"))
os.makedirs(OUT, exist_ok=True)
C, F, E = S.CLEAN, S.FINAL, S.EMPIRICAL
n, N, nE = len(C), len(F), len(E)
P = S.pct


def esc(s):
    return s.replace("&", r"\&").replace("%", r"\%")


def block(title, items, denom):
    lines = [rf"\multicolumn{{3}}{{@{{}}l}}{{\textit{{{title}}}}} \\"]
    for label, k in items:
        lines.append(rf"\quad {esc(label)} & {k} & {P(k, denom)} \\")
    return "\n".join(lines) + "\n\\addlinespace"


def counts(rows, field, order, rename=None, rest="Other"):
    c = Counter(r[field] for r in rows)
    out = [((rename or {}).get(k, k), c.get(k, 0)) for k in order if c.get(k, 0)]
    other = sum(v for k, v in c.items() if k not in order)
    if other:
        out.append((rest, other))
    return out


def yes(rows, field):
    return sum(r[field] == "Yes" for r in rows)


# ── Table 1 ──────────────────────────────────────────────────────────────────
tc = Counter(S.topic(r) for r in C)
main_topics = ["Mechanics", "Oscillations & Waves", "Electromagnetism", "Optics"]
other_topics = [(t, tc[t]) for t in S.TOPIC_ORDER if t not in main_topics and tc.get(t)]
lv = Counter()
for r in C:
    for k, v in S.level_flags(r).items():
        lv[k] += v
sw = Counter(r["Software (main)"] for r in C)
sw_other = n - sum(sw.get(k, 0) for k in ("Tracker", "Logger Pro", "COACH", "Viana", "Not stated"))
parts = [
    block(f"Physics topic ($n = {n}$)", [(t.replace("&", "and").replace("Oscillations and Waves", "Oscillations and waves"), tc.get(t, 0))
                                         for t in main_topics] + [("Other$^{a}$", sum(k for _, k in other_topics))], n),
    block(f"Software ($n = {n}$)", [("Tracker", sw.get("Tracker", 0)), ("Logger Pro", sw.get("Logger Pro", 0)),
                                   ("COACH or Viana", sw.get("COACH", 0) + sw.get("Viana", 0)), ("Other tools", sw_other),
                                   ("Not stated", sw.get("Not stated", 0))], n),
    block(f"Paper type ($n = {n}$)", counts(C, "Paper type", ["Activity description", "Implementation report",
                                                               "Empirical study with students", "Accuracy or methods study"],
                                          {"Empirical study with students": "Empirical study with students"}), n),
    block(f"Recording hardware ($n = {n}$)", counts(C, "Recording hardware", ["Smartphone", "Digital camera", "High-speed camera",
                                                                             "Tablet", "Webcam", "Not stated"]), n),
    block(f"Setting ($n = {n}$)", counts(C, "Setting", ["Lab", "Classroom", "Online / home", "Outdoor", "Not stated"],
                                       {"Lab": "Laboratory"}), n),
    block(f"Educational level ($n = {n}$)", [("Middle school", lv["Middle school"]), ("High school", lv["High school"]),
                                            ("Undergraduate (any)", lv["Undergraduate (any)"]),
                                            (r"\quad of which introductory", lv["Undergraduate introductory"]),
                                            ("Teacher education", lv["Teachers / teacher education"]),
                                            ("Not stated", lv["Not specified"])], n),
    block(f"Video subject ($n = {n}$)", counts(C, "Video subject", ["Real-world objects", "Standard lab equipment", "Student-produced",
                                                                   "Archival / professional footage"],
                                             {"Standard lab equipment": "Standard laboratory equipment"}), n),
]
foot = ", ".join(f"{t.replace('&', 'and').lower()} ({k})" for t, k in other_topics)
with open(os.path.join(OUT, "table_summary.tex"), "w", encoding="utf-8") as f:
    f.write(rf"""\begin{{table}}[htbp]
\caption{{Summary characteristics of the {N} included papers. Educational level is not mutually exclusive: papers addressing several levels are counted under each. Category definitions are given in Supplementary Material S2--S3.}}
\label{{tab:summary}}
\small
\begin{{tabular}}{{@{{}}lrr@{{}}}}
\toprule
Characteristic & $n$ & \% \\
\midrule
""" + "\n".join(parts).removesuffix("\n\\addlinespace") + rf"""
\bottomrule
\end{{tabular}}

\smallskip
{{\footnotesize $^{{a}}${esc(foot)}.}}
\end{{table}}
""")

# ── Table 2: practice (block A) ──────────────────────────────────────────────
used = [r for r in C if r["Implemented with students?"] == "Used with students"]
fr = sum(bool(r["Frame rate"]) and not r["Frame rate"].lower().startswith("not") for r in C)
anycheck = sum(any(r[f] == "Yes" for f in ("Checked against accepted/theoretical value?", "Checked against other instrument?",
                                           "Checked against simulation/model?")) for r in C)
role = Counter(r["Students' role"] for r in C)
unc = Counter(r["Uncertainty analysis"] for r in C)
rows2 = [
    block("Use with students", [("Used with real students", len(used)),
                                ("Proposed only", sum(r["Implemented with students?"] == "Proposed only" for r in C)),
                                ("Unclear", sum(r["Implemented with students?"] == "Unclear" for r in C))], n),
    block("Students' role with the video", [(k, role.get(k, 0)) for k in ("Record own video", "Analyse provided video",
                                                                          "Watch demonstration", "None (authors only)", "Unclear")
                                            if role.get(k, 0)], n),
    block("Measurement reporting", [("Frame rate reported", fr), ("Length calibration described", yes(C, "Calibration described?")),
                                    ("Quantitative uncertainty analysis", unc.get("Quantitative", 0)),
                                    ("Uncertainty discussed in words only", unc.get("Qualitative", 0)),
                                    ("No uncertainty analysis", unc.get("None", 0))], n),
    block("Validation of the video data", [("Against an accepted or theoretical value", yes(C, "Checked against accepted/theoretical value?")),
                                           ("Against another instrument", yes(C, "Checked against other instrument?")),
                                           ("Against a simulation or model", yes(C, "Checked against simulation/model?")),
                                           ("Any of these", anycheck)], n),
    block("Other features", [("Dynamical or computational model built", yes(C, "Model building?")),
                             ("Videos, data or materials shared", yes(C, "Materials shared?")),
                             ("Remote, online or home context", yes(C, "Remote/home context?"))], n),
]
with open(os.path.join(OUT, "table_practice.tex"), "w", encoding="utf-8") as f:
    f.write(rf"""\begin{{table}}[htbp]
\caption{{How the video-analysis activities were implemented and how the measurements were reported, for the {n} full-text papers. Categories within a panel are mutually exclusive except under validation, where a paper can report several checks.}}
\label{{tab:practice}}
\small
\begin{{tabular}}{{@{{}}lrr@{{}}}}
\toprule
 & $n$ & \% \\
\midrule
""" + "\n".join(rows2).removesuffix("\n\\addlinespace") + r"""
\bottomrule
\end{tabular}
\end{table}
""")

# ── Table 3: evidence map (block B) ──────────────────────────────────────────
DESIGNS = [("One-group pre/post", "Pre/post"), ("Comparison group (non-randomised)", "Non-rand."),
           ("Randomised comparison", "Rand."), ("Qualitative", "Qual."), ("Survey only", "Survey"), ("Other", "Other")]
OUTCOMES = ["Conceptual understanding", "Graph interpretation", "Lab or inquiry skills", "Problem solving",
            "Attitudes, motivation or engagement", "Other"]
SYM = {"Positive": "+", "Null": "0", "Mixed": r"$\pm$", "Negative": r"$-$", "Not reported": "?"}


def cell(rows):
    if not rows:
        return "--"
    c = Counter(r["B: Result"] for r in rows)
    detail = " ".join(f"{SYM[k]}{c[k]}" for k in ("Positive", "Null", "Mixed", "Negative", "Not reported") if c.get(k))
    return rf"{len(rows)} \scriptsize({detail})"


lines = []
for o in OUTCOMES:
    rows_o = [r for r in E if r["B: Outcome (main)"] == o]
    if not rows_o:
        continue
    lines.append(f"{esc(o)} & " + " & ".join(cell([r for r in rows_o if r["B: Design"] == d]) for d, _ in DESIGNS)
                 + f" & {len(rows_o)} \\\\")
tot = " & ".join(str(sum(r["B: Design"] == d for r in E)) for d, _ in DESIGNS)
res = Counter(r["B: Result"] for r in E)
es = sum(bool(r["B: Effect size"]) and not r["B: Effect size"].lower().startswith("not") for r in E)
with open(os.path.join(OUT, "table_evidence_map.tex"), "w", encoding="utf-8") as f:
    f.write(rf"""\begin{{table}}[htbp]
\caption{{Evidence map of the {nE} empirical studies with students: main outcome measured by study design. Each cell gives the number of studies and, in brackets, the direction of the main result for the video-analysis condition (+ positive, 0 null, $\pm$ mixed, $-$ negative, ? not reported). {(' No study had ' + ', '.join(o.lower() for o in OUTCOMES if not any(r['B: Outcome (main)'] == o for r in E)) + ' as its main outcome.') if any(not any(r['B: Outcome (main)'] == o for r in E) for o in OUTCOMES) else ''} Overall, {res.get('Positive', 0)} studies reported a positive result{'; none reported a null result' if not res.get('Null') else ''}; {es} reported an effect size.}}
\label{{tab:evidence}}
\footnotesize
\resizebox{{\textwidth}}{{!}}{{%
\begin{{tabular}}{{@{{}}l{'c' * len(DESIGNS)}r@{{}}}}
\toprule
Main outcome & {' & '.join(s for _, s in DESIGNS)} & Total \\
\midrule
""" + "\n".join(lines) + rf"""
\midrule
Total & {tot} & {nE} \\
\bottomrule
\end{{tabular}}}}
\end{{table}}
""")
print(f"tables written to {OUT}: table_summary.tex, table_practice.tex, table_evidence_map.tex")
