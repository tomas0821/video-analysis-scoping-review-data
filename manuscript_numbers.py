"""
Print every statistic reported in the manuscript (text, tables, captions) from
review_stats.py, so each number in main.tex can be checked against the data.
Usage: python manuscript_numbers.py          (REVIEW_DATASET=... for a test build)
"""
import re
import statistics
from collections import Counter

import review_stats as S

R, F, C, E = S.ROWS, S.FINAL, S.CLEAN, S.EMPIRICAL
n, N = len(C), len(F)


def show(title, counts, denom):
    print(f"\n{title} (n = {denom})")
    for k, v in counts:
        print(f"  {k:40s} {v:4d}  {S.pct(v, denom):3d}%")


def ordered(rows, field, order=None):
    c = Counter(r[field] for r in rows)
    keys = order or [k for k, _ in c.most_common()]
    return [(k, c.get(k, 0)) for k in keys] + [(k, v) for k, v in c.items() if order and k not in order]


def yes(rows, field):
    return sum(r[field] == "Yes" for r in rows)


def num(s):
    m = re.search(r"\d+(\.\d+)?", s or "")
    return float(m.group()) if m else None


print("=== PRISMA ===")
ft, ta = S.FT_ALL, [r for r in R if r["Screened_on"] != "Full text"]
print(f"records screened {S.SCREENED}: full text {len(ft)} ({S.pct(len(ft), S.SCREENED)}%), title/abstract {len(ta)}")
for name, rows in (("full text", ft), ("title/abstract", ta)):
    inc = [r for r in rows if r["Decision"] == "Include"]
    print(f"  {name}: included {len(inc)}, excluded {len(rows) - len(inc)}; reasons "
          f"{Counter(r['Exclusion_reason'] for r in rows if r['Decision'] == 'Exclude').most_common()}")
print(f"included {N} (full text only); reports not retrieved {len(S.NOT_RETRIEVED)}, of which eligible on title/abstract {len(S.TA_INC)}")

print("\n=== YEARS (all included; full-text) ===")
ya, yf = Counter(S.year_of(r) for r in F), Counter(S.year_of(r) for r in C)
for y in sorted(k for k in ya if k):
    print(f"  {y}: {ya[y]:3d}  ft {yf[y]:3d}")
yrs = [y for y in ya if y]
print(f"  first year {min(yrs)}; peak {max(ya, key=ya.get)} ({max(ya.values())}); "
      f"2017-19 {[ya[y] for y in (2017, 2018, 2019)]}; 2020-25 {[ya[y] for y in range(2020, 2026)]}")

show("Topic", ordered(C, "Physics topic", S.TOPIC_ORDER), n)
mech = [r for r in C if S.topic(r) == "Mechanics"]
show("Mechanics subtopic", ordered(mech, "Mechanics subtopic", S.SUBTOPIC_ORDER), len(mech))
print("  several topics:", yes(C, "Several topics?"))

show("Software (coded)", ordered(C, "Software (main)"), n)
show("Software (bucketed)", S.counter(C, lambda r: S.bucket_sw(r["Software (main)"])).most_common(), n)
for t in S.TOPIC_ORDER:
    rows = [r for r in C if S.topic(r) == t]
    if rows:
        k = sum(r["Software (main)"] == "Tracker" for r in rows)
        print(f"  Tracker share in {t:26s} {k:3d}/{len(rows):3d} = {S.pct(k, len(rows))}%")
by_year = {}
for r in C:
    by_year.setdefault(S.year_of(r), []).append(r["Software (main)"] == "Tracker")
print("  Tracker share by year:", {y: f"{sum(v)}/{len(v)}" for y, v in sorted(by_year.items()) if y})

show("Paper type", ordered(C, "Paper type", ["Activity description", "Implementation report",
                                             "Empirical study with students", "Accuracy or methods study", "Other"]), n)
show("Stated aim (main)", ordered(C, "Stated aim (main)"), n)
aims = Counter(a for r in C for a in {r["Stated aim (main)"], r["Stated aim (second)"]} if a and a != "Not stated")
show("Stated aims (main or second, non-exclusive)", aims.most_common(), n)
show("Recording hardware", ordered(C, "Recording hardware"), n)
show("Setting", ordered(C, "Setting"), n)
show("Video subject", ordered(C, "Video subject"), n)
lv = Counter()
for r in C:
    for k, v in S.level_flags(r).items():
        lv[k] += v
show("Educational level (non-exclusive)", lv.most_common(), n)

print("\n=== BLOCK A (every included full text) ===")
show("Implemented with students", ordered(C, "Implemented with students?"), n)
used = [r for r in C if r["Implemented with students?"] == "Used with students"]
ns = [num(r["Students (n)"]) for r in used if num(r["Students (n)"])]
print(f"  students reported in {len(ns)}/{len(used)} implemented papers; median {statistics.median(ns) if ns else '-'}")
show("Students' role", ordered(C, "Students' role"), n)
fr = [r for r in C if r["Frame rate"] and not r["Frame rate"].lower().startswith("not")]
show("Frame rate reported", [("reported", len(fr))], n)
for f in ("Calibration described?", "Checked against accepted/theoretical value?", "Checked against other instrument?",
          "Checked against simulation/model?", "Model building?", "Materials shared?", "Remote/home context?"):
    show(f, [("Yes", yes(C, f))], n)
anycheck = sum(any(r[f] == "Yes" for f in ("Checked against accepted/theoretical value?", "Checked against other instrument?",
                                           "Checked against simulation/model?")) for r in C)
show("Checked against anything", [("Yes", anycheck)], n)
show("Uncertainty analysis", ordered(C, "Uncertainty analysis", ["Quantitative", "Qualitative", "None"]), n)
show("Language", ordered(C, "Language"), n)

print(f"\n=== BLOCK B (empirical studies with students, n = {len(E)}) ===")
for f in ("B: Design", "B: Comparison condition", "B: Sample level", "B: Outcome (main)", "B: Instrument (main)", "B: Result", "B: Duration"):
    show(f, ordered(E, f), len(E))
ss = [num(r["B: Sample (n)"]) for r in E if num(r["B: Sample (n)"])]
print(f"  sample reported {len(ss)}/{len(E)}; median {statistics.median(ss) if ss else '-'}; range {min(ss) if ss else '-'}-{max(ss) if ss else '-'}")
es = [r for r in E if r["B: Effect size"] and not r["B: Effect size"].lower().startswith("not")]
print(f"  effect size reported {len(es)}/{len(E)}")
comp = [r for r in E if r["B: Design"] in ("Comparison group (non-randomised)", "Randomised comparison")]
print(f"  with a comparison group {len(comp)}/{len(E)}")
std = [r["B: Instrument names"] for r in E if r["B: Instrument (main)"] == "Standardised test"]
print(f"  standardised tests: {std}")

print("\n=== VENUES (all included, normalised) ===")
vc = Counter(S.venue(r["Venue"]) for r in F)
for v, k in vc.most_common(10):
    print(f"  {k:3d} {S.pct(k, N):3d}%  {v}")
top3 = sum(k for _, k in vc.most_common(3))
print(f"  top-3 {top3}/{N} = {S.pct(top3, N)}%; distinct venues {len(vc)}")

print("\n=== COUNTRIES (all included with affiliation data) ===")
cc, with_aff = Counter(), 0
for r in F:
    cs = S.countries_of(r)
    with_aff += bool(cs)
    cc.update(cs)
print(f"  papers with affiliation data: {with_aff}/{N}; distinct countries {len(cc)}")
print("  top:", cc.most_common(12))
for name, region in (("Africa", S.AFRICA), ("South Asia", S.SOUTH_ASIA),
                     ("Middle East", S.MIDDLE_EAST), ("Latin America", S.LATAM)):
    papers = [r for r in F if set(S.countries_of(r)) & region]
    print(f"  {name}: {len(papers)} papers; countries {sorted(set(c for r in papers for c in S.countries_of(r)) & region)}")
print("\n  country x topic (full-text papers, top 8 countries):")
cft = Counter(c for r in C for c in S.countries_of(r))
for c, k in cft.most_common(8):
    rows = [r for r in C if c in S.countries_of(r)]
    m = sum(S.topic(r) == "Mechanics" for r in rows)
    print(f"    {c:26s} {k:3d}  mechanics {m:3d} ({S.pct(m, k)}%)  "
          f"top non-mech {Counter(S.topic(r) for r in rows if S.topic(r) != 'Mechanics').most_common(2)}")

print("\n=== OTHER ===")
print(f"  included papers without DOI: {sum(1 for r in F if not r['DOI'])}/{N}")
