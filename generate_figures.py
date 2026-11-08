"""
Generate all manuscript figures as PDFs using matplotlib.

All figures are computed from the dataset through review_stats.py (no
hardcoded counts), which also feeds manuscript_numbers.py, so figures, Table 1
and the text share one set of rules (documented in Supplementary S3):

  - Topic:    harmonised Broad_Topic / Mechanics_Subtopic coding
              (topic_harmonised_20261018.csv), full-text papers.
  - Software: Tracker > Logger Pro > COACH > Viana > Not specified > Other
              (first match wins).
  - Years, venues, countries: all included papers. Countries come from the
              extraction for full-text papers and from the bibliographic
              affiliations for abstract-only papers.

Output: manuscript/figures/*.pdf
Requires internet access + geopandas for the choropleth map (Natural Earth
shapefile fetched from naciscdn.org at runtime).
"""

import os
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

import review_stats as S

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("REVIEW_FIGDIR", os.path.join(BASE, "manuscript", "figures"))
os.makedirs(OUT_DIR, exist_ok=True)

# Dimensions: interact.cls textwidth = 34pc ≈ 5.68in; 0.9x ≈ 5.11in
TW = 5.11   # 0.9 * textwidth in inches
FS = 8.5    # footnotesize equivalent

plt.rcParams.update({
    "font.family": "serif",
    "font.size": FS,
    "axes.labelsize": FS,
    "xtick.labelsize": FS,
    "ytick.labelsize": FS,
    "legend.fontsize": FS - 0.5,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
})

BLUE = "#4472C4"
RED = "#C0504D"
GREEN = "#9BBB59"
GRAY = "#808080"
ORANGE = "#F79646"
LIGHT = "#BFCFEA"


def save(fig, name):
    path = os.path.join(OUT_DIR, f"{name}.pdf")
    fig.savefig(path, format="pdf")
    plt.close(fig)
    print(f"  {name}.pdf")


CLEAN, FINAL = S.CLEAN, S.FINAL
N_FT, N_ALL = len(CLEAN), len(FINAL)
print(f"Data: {N_ALL} included ({N_FT} full-text)")


def barh(counts_labels, name, height=2.2, colors=None):
    labels = [l for l, _ in counts_labels]
    vals = [v for _, v in counts_labels]
    fig, ax = plt.subplots(figsize=(TW, height))
    y = np.arange(len(labels))
    bars = ax.barh(y, vals, height=0.5, color=colors or BLUE, alpha=0.75)
    ax.bar_label(bars, padding=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.set_xlabel("Number of papers")
    ax.set_xlim(0, max(vals) * 1.15)
    ax.invert_yaxis()
    save(fig, name)


# ── Fig: Publication years (all included, stacked by screening pathway) ─────
ya = Counter(S.year_of(r) for r in FINAL)
yf = Counter(S.year_of(r) for r in CLEAN)
y0, y1 = min(ya), max(ya)
years = list(range(y0, y1 + 1))
ft_vals = [yf.get(y, 0) for y in years]
ab_vals = [ya.get(y, 0) - yf.get(y, 0) for y in years]
tot = [a + b for a, b in zip(ft_vals, ab_vals)]
ma_years = [y for y in years[1:-1] if y + 1 < S.SEARCH_YEAR]      # MA excludes partial year
ma_vals = [round(sum(tot[years.index(y) - 1:years.index(y) + 2]) / 3, 1) for y in ma_years]
print(f"  years: peak {max(ya.values())} in {max(ya, key=ya.get)}")

fig, ax = plt.subplots(figsize=(TW, 2.4))
ax.bar(years, ft_vals, width=0.7, color=BLUE, alpha=0.8, label="Included papers")
if any(ab_vals):
    ax.bar(years, ab_vals, width=0.7, bottom=ft_vals, color=LIGHT, label="Abstract only")
ax.plot(ma_years, ma_vals, color=RED, linewidth=1.5, linestyle="--", label="3-year mean")
ax.axvspan(2019.5, 2021.5, alpha=0.13, color=GRAY)
ax.text(2020.5, max(tot) + 2, "COVID-19", fontsize=6.5, color=GRAY, ha="center")
ax.text(S.SEARCH_YEAR, tot[-1] + 0.8, "partial (to May)", fontsize=5.5, color=GRAY, ha="center", va="bottom", rotation=90)
ax.set_xlim(y0 - 0.8, y1 + 1.4)
ax.set_xlabel("Year")
ax.set_ylabel("Number of papers")
ax.set_xticks([y for y in years if y % 2 == 1])
ax.tick_params(axis="x", rotation=45)
ax.set_ylim(0, max(tot) + 7)
ax.legend(loc="upper left")
save(fig, "fig_years")

# ── Fig: Physics topics (harmonised) ─────────────────────────────────────────
tc = Counter(S.topic(r) for r in CLEAN)
print(f"  topics: {dict(tc)}")
barh([(t, tc.get(t, 0)) for t in S.TOPIC_ORDER if tc.get(t, 0)], "fig_topics", 2.3)

# ── Fig: Software tools ──────────────────────────────────────────────────────
SW_ORDER = ["Tracker", "Other", "Logger Pro", "Not specified", "COACH", "Viana"]
swc = Counter(S.bucket_sw(r["Video_Analysis_Software"]) for r in CLEAN)
print(f"  software: {dict(swc)}")
barh([(s, swc.get(s, 0)) for s in SW_ORDER], "fig_software", 2.0)

# ── Fig: Heatmap — Topics × Software ─────────────────────────────────────────
HM_TOPICS = ["Mechanics", "Oscill. & Waves", "EM", "Optics", "Thermo. & Fluids", "Other"]
HM_KEY = {"Mechanics": 0, "Oscillations & Waves": 1, "Electromagnetism": 2, "Optics": 3,
          "Thermodynamics": 4, "Fluids": 4, "Modern & Nuclear Physics": 5,
          "Astronomy": 5, "Other": 5}
HM_SW = ["Tracker", "Other", "Logger Pro", "Not specified", "COACH", "Viana"]
hm_ts = np.zeros((len(HM_TOPICS), len(HM_SW)), dtype=int)
for r in CLEAN:
    hm_ts[HM_KEY[S.topic(r)], HM_SW.index(S.bucket_sw(r["Video_Analysis_Software"]))] += 1
print(f"  heatmap topics×software: max={hm_ts.max()}, mechanics+Tracker={hm_ts[0,0]}/{hm_ts[0].sum()}")


def heatmap(mat, rows, cols, name, title, height, totals=False):
    fig, ax = plt.subplots(figsize=(TW, height))
    ax.imshow(mat, cmap="Blues", aspect="auto", vmin=0, vmax=mat.max())
    ax.set_xticks(np.arange(len(cols)))
    ax.set_xticklabels(cols, fontsize=7.5)
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels(rows, fontsize=7.5)
    for i in range(len(rows)):
        for j in range(len(cols)):
            v = mat[i, j]
            if v > 0:
                ax.text(j, i, str(v), ha="center", va="center", fontsize=7,
                        color="white" if v > mat.max() * 0.55 else "black")
    if totals:
        for i in range(len(rows)):
            ax.text(len(cols) - 0.42, i, f"n={mat[i].sum()}", ha="left", va="center",
                    fontsize=6.5, color="gray")
        ax.set_xlim(-0.5, len(cols) + 0.25)
    ax.set_title(title, fontsize=FS)
    save(fig, name)


heatmap(hm_ts, HM_TOPICS, ["Tracker", "Other", "Logger Pro", "Not spec.", "COACH", "Viana"],
        "fig_heatmap_ts", f"Physics topics vs. software tools (n={hm_ts.sum()})", 2.3)

# ── Fig: Research design ─────────────────────────────────────────────────────
DESIGNS = S.DESIGN_ORDER
dc = Counter(S.bucket_design(r["Research_Design"]) for r in CLEAN)
print(f"  design: {dict(dc)}")
fig, ax = plt.subplots(figsize=(TW * 0.85, 1.6))
for i, (d, col) in enumerate(zip(DESIGNS, [BLUE, ORANGE, RED, GREEN, GRAY])):
    bar = ax.barh(i, dc.get(d, 0), height=0.5, color=col, alpha=0.75)
    ax.bar_label(bar, padding=3)
ax.set_yticks(np.arange(len(DESIGNS)))
ax.set_yticklabels(DESIGNS)
ax.set_xlabel("Number of papers")
ax.set_xlim(0, max(dc.values()) * 1.18)
ax.invert_yaxis()
save(fig, "fig_design")

# ── Country counts (all included papers with affiliation data) ──────────────
country_counts = Counter()
rows_with_aff = 0
for r in FINAL:
    cs = S.countries_of(r)
    rows_with_aff += bool(cs)
    for c in cs:
        country_counts[c] += 1
print(f"  countries: {len(country_counts)} distinct, {rows_with_aff}/{N_ALL} papers with affiliation data")
print(f"    top: {country_counts.most_common(8)}")

# ── Fig: Countries — world map choropleth ────────────────────────────────────
import geopandas as gpd
import matplotlib.colors as mcolors

# 50m scale: includes small states (e.g. Singapore) missing at 110m
_url = "https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip"
world = gpd.read_file(_url)
world = world[world["NAME"] != "Antarctica"]

ne_names = set(world["NAME"])
NE_ALIAS = {"Czech Republic": "Czechia", "South Korea": "South Korea", "United States": "United States of America", "Bosnia and Herzegovina": "Bosnia and Herz."}
for ours, ne in NE_ALIAS.items():
    if ours in country_counts and ours not in ne_names and ne in ne_names:
        country_counts[ne] = country_counts.pop(ours)
if "South Korea" in country_counts and "South Korea" not in ne_names and "Korea" in ne_names:
    country_counts["Korea"] = country_counts.pop("South Korea")
world["papers"] = world["NAME"].map(country_counts).fillna(0).astype(int)
unmapped = set(country_counts) - ne_names
if unmapped:
    print(f"    WARNING: countries not on map: {unmapped}")

EU_X0, EU_X1, EU_Y0, EU_Y1 = -15, 42, 34, 72


def is_european(row):
    cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
    return EU_X0 <= cx <= EU_X1 and EU_Y0 <= cy <= EU_Y1


world["in_europe"] = world.apply(is_european, axis=1)
vmax = world["papers"].max()
norm = mcolors.Normalize(0, vmax)
cmap = plt.cm.Blues


import matplotlib.patheffects as pe
LABEL_SHIFT = {"Portugal": (-1.2, 0.0), "Spain": (0.8, 0.0)}   # degrees; keeps the two Iberian labels apart
LABEL_AT = {"Indonesia": (113.5, -1.5), "Malaysia": (102.0, 4.0), "Thailand": (100.5, 16.5)}   # lon, lat: crowded SE Asia


def draw_map(ax, xlim, ylim, label_europe, fontsize=5.5):
    world[world["papers"] == 0].plot(ax=ax, color="#E8E8E8", edgecolor="white", linewidth=0.3)
    world[world["papers"] > 0].plot(ax=ax, column="papers", cmap=cmap, norm=norm,
                                    edgecolor="white", linewidth=0.3, legend=False)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_axis_off()
    for _, row in world[world["papers"] > 0].iterrows():
        if row["in_europe"] and not label_europe:
            continue
        geom = row.geometry
        if geom.geom_type == "MultiPolygon":                      # label the largest landmass (e.g. not the sea between islands)
            geom = max(geom.geoms, key=lambda g: g.area)
        pt = geom.representative_point()
        cx, cy = pt.x + LABEL_SHIFT.get(row["NAME"], (0, 0))[0], pt.y + LABEL_SHIFT.get(row["NAME"], (0, 0))[1]
        if row["NAME"] in LABEL_AT and not label_europe:
            cx, cy = LABEL_AT[row["NAME"]]
        if not (xlim[0] <= cx <= xlim[1] and ylim[0] <= cy <= ylim[1]):
            continue
        n = row["papers"]
        dark = n >= 20
        ax.text(cx, cy, str(n), ha="center", va="center", fontsize=fontsize, fontweight="bold",
                color="white" if dark else "black",
                path_effects=[pe.withStroke(linewidth=1.6, foreground="#1F3B73" if dark else "white")])


fig = plt.figure(figsize=(TW * 1.1, TW * 0.5), facecolor="white")
gs = fig.add_gridspec(1, 2, width_ratios=[2, 1], wspace=0.04)
ax_world = fig.add_subplot(gs[0])
ax_eu = fig.add_subplot(gs[1])
draw_map(ax_world, (-160, 180), (-55, 80), label_europe=False, fontsize=5.5)
rect = plt.Rectangle((EU_X0, EU_Y0), EU_X1 - EU_X0, EU_Y1 - EU_Y0, linewidth=0.9,
                     edgecolor="#555555", facecolor="none", transform=ax_world.transData,
                     zorder=5, linestyle="--")
ax_world.add_patch(rect)
ax_world.set_title("(a) World", fontsize=FS, loc="left", pad=2)
draw_map(ax_eu, (EU_X0, EU_X1), (EU_Y0, EU_Y1), label_europe=True, fontsize=6)
ax_eu.set_title("(b) Europe", fontsize=FS, loc="left", pad=2)
for spine in ax_eu.spines.values():
    spine.set_visible(True)
    spine.set_edgecolor("#AAAAAA")
    spine.set_linewidth(0.6)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=[ax_world, ax_eu], orientation="horizontal", fraction=0.03,
                    pad=0.02, aspect=40, shrink=0.5, anchor=(0.3, 1.0))
cbar.set_label("Number of papers", fontsize=7)
cbar.ax.tick_params(labelsize=6.5)
save(fig, "fig_countries")

# ── Fig: Heatmap — Countries × Topics (full-text papers: topics need text) ──
DISPLAY = {"United States of America": "USA"}
cc_ft = Counter(c for r in CLEAN for c in S.countries_of(r))
c_rows_full = [c for c, _ in cc_ft.most_common(8)]
CT_COLS = ["Mechanics", "Oscill.\n& Waves", "EM", "Optics", "Thermo.\n& Fluids", "Other"]
hm_ct = np.zeros((len(c_rows_full), len(CT_COLS)), dtype=int)
for r in CLEAN:
    for c in S.countries_of(r):
        if c in c_rows_full:
            hm_ct[c_rows_full.index(c), HM_KEY[S.topic(r)]] += 1
print(f"  heatmap countries×topics: max={hm_ct.max()}, rows={dict(zip(c_rows_full, hm_ct.sum(axis=1).tolist()))}")
heatmap(hm_ct, [DISPLAY.get(c, c) for c in c_rows_full], CT_COLS, "fig_heatmap_ct",
        "Countries vs. physics topics (full-text papers)", 2.8)

# ── Fig: Publication venues (all included, normalised names) ─────────────────
ABBREV = {
    "Physics Education": "Physics Education",
    "The Physics Teacher": "The Physics Teacher",
    "European Journal of Physics": "Eur. J. Phys.",
    "Journal of Physics: Conference Series": "JPCS",
    "Revista Brasileira de Ensino de Física": "Rev. Bras. Ens. Fís.",
    "AIP Conference Proceedings": "AIP Conf. Proc.",
    "American Journal of Physics": "Am. J. Phys.",
}
jc = Counter(S.venue(r["Journal"]) for r in FINAL)
named = sorted([j for j in ABBREV if jc.get(j, 0)], key=lambda j: -jc[j])
others = [j for j in jc if j not in ABBREV]
n_real = len([j for j in others if j != "Not mentioned"])
labels = [(ABBREV[j], jc[j]) for j in named] + [(f"Other ({n_real} venues" + (f"; {jc['Not mentioned']} unrecorded)" if jc.get('Not mentioned') else ")"),
                                                 sum(jc[j] for j in others))]
print(f"  journals: {dict(labels)}")
barh(labels, "fig_journals", 2.2)

# ── Fig: Software over time (stacked area, full-text papers) ─────────────────
SW_TIME = ["Tracker", "Logger Pro", "Not specified", "Other"]
ft_years = list(range(min(yf), max(yf) + 1))
series = {g: [0] * len(ft_years) for g in SW_TIME}
for r in CLEAN:
    b = S.bucket_sw(r["Video_Analysis_Software"])
    g = b if b in ("Tracker", "Logger Pro", "Not specified") else "Other"
    series[g][ft_years.index(S.year_of(r))] += 1
fig, ax = plt.subplots(figsize=(TW, 2.2))
ax.stackplot(ft_years, *[series[g] for g in SW_TIME], labels=SW_TIME,
             colors=[BLUE, GREEN, "#BFBFBF", ORANGE], alpha=0.8)
ax.set_xlabel("Year")
ax.set_ylabel("Number of papers")
ax.set_xlim(ft_years[0], ft_years[-1])
ax.set_ylim(0, max(sum(v) for v in zip(*series.values())) + 7)
ax.legend(loc="upper left", fontsize=7)
save(fig, "fig_sw_time")

# ── Fig: Mechanics subtopics × Software (all mechanics papers) ───────────────
MECH = [r for r in CLEAN if S.topic(r) == "Mechanics"]
subs = [s for s in S.SUBTOPIC_ORDER if any(S.subtopic(r) == s for r in MECH)]
MSW = ["Tracker", "Logger Pro", "COACH", "Viana", "Not specified", "Other"]
hm = np.zeros((len(subs), len(MSW)), dtype=int)
for r in MECH:
    hm[subs.index(S.subtopic(r)), MSW.index(S.bucket_sw(r["Video_Analysis_Software"]))] += 1
print(f"  mechanics subtopic heatmap: n={hm.sum()} (all {len(MECH)} mechanics papers)")
heatmap(hm, [s.replace(" Motion", "") if s.startswith("Circular") else s for s in subs], MSW,
        "fig_heatmap_mechanics", f"Mechanics subtopics vs. software tools (n={hm.sum()})",
        3.1, totals=True)

print(f"\nDone — {len(os.listdir(OUT_DIR))} PDFs in {OUT_DIR}")
