#!/usr/bin/env bash
# Rebuild every result in the manuscript from one coding workbook, in one step.
#   ./rebuild_results.sh                                   final build: manual_coding/coding_FINAL.xlsx -> manuscript/
#   ./rebuild_results.sh <workbook.xlsx> <output dir>      test build: everything goes to <output dir> (figures/, tex/, numbers.txt)
# Needs: python3 with openpyxl; a Python with geopandas + matplotlib for the figures (default ~/.venvs/scoping-review).
set -euo pipefail
cd "$(dirname "$0")"
CODING="${1:-manual_coding/coding_FINAL.xlsx}"
OUTDIR="${2:-}"
FIGPY="${FIGPY:-$HOME/.venvs/scoping-review/bin/python}"
if [ -n "$OUTDIR" ]; then
  export REVIEW_DATASET="$OUTDIR/coded_dataset.csv" REVIEW_FIGDIR="$OUTDIR/figures" REVIEW_TEXDIR="$OUTDIR/tex"
  NUMBERS="$OUTDIR/numbers.txt"
else
  export REVIEW_DATASET="final_coding/coded_dataset.csv" REVIEW_FIGDIR="manuscript/figures" REVIEW_TEXDIR="manuscript"
  NUMBERS="final_coding/manuscript_numbers.txt"
fi
mkdir -p "$(dirname "$REVIEW_DATASET")" "$REVIEW_FIGDIR" "$REVIEW_TEXDIR"
python3 build_dataset.py --coding "$CODING" --out "$REVIEW_DATASET"
python3 manuscript_numbers.py > "$NUMBERS"
python3 make_results_tables.py
python3 make_supplementary_table.py
python3 make_charting_fields_table.py
"$FIGPY" generate_figures.py > /dev/null
echo "Done. Numbers to check against main.tex: $NUMBERS"
