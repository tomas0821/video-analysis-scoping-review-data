# Video analysis as a pedagogical tool in physics education: a scoping review — data and code

**Tomas Rojas**¹ ([ORCID 0000-0001-5745-4255](https://orcid.org/0000-0001-5745-4255)), **Eduardo Arias Navarro**¹ ² ([ORCID 0000-0002-8293-7686](https://orcid.org/0000-0002-8293-7686)) and **Esteban Jiménez Moya**¹ ([ORCID 0000-0001-7712-3197](https://orcid.org/0000-0001-7712-3197))
¹ Universidad de Costa Rica, Sede de Occidente, San Ramón, Costa Rica
² Universidad Estatal a Distancia, San Pedro de Montes de Oca, Costa Rica

This repository accompanies the scoping review *Video analysis as a pedagogical tool in physics education: a scoping review* (submitted to *Research in Science & Technological Education*). The review maps the literature on video-based motion analysis (the frame-by-frame tracking of objects in digital video to extract quantitative physical data) in physics teaching, following PRISMA-ScR.

The repository holds:
- the search strings;
- the coding protocol;
- the list of screened records;
- the code that turns the final coding into every number, table and figure in the article.

> **Status.** The charted dataset, the screening decisions and the agreement between coders will be added here when the coding is complete. The archived release will be cited in the article with its DOI.

## Contents

| Path | What it is |
|---|---|
| `search/` | Search strings for Scopus, Web of Science Core Collection and ERIC (EBSCOhost); records published from 2000 onward, searched 19–20 May 2026 |
| `protocol/coding_guide.md` | The coding guide given to every coder: eligibility criteria, decision rules, charting rules and the answer list of every field |
| `data/records.csv` | The 419 screened records after deduplication and removal of book chapters. Fields: `ID`, `Bib_Key`, first author, year, title, venue, DOI, and the countries named in the affiliation field of the bibliographic record |
| `coding_form.py` | The coding form (fields, answer lists, guide text), defined once and imported by the scripts below |
| `merge_coding.py` | Compares the coders' workbooks (agreement, Cohen's kappa), lists the disagreements to resolve, and builds the final workbook |
| `build_dataset.py` | Final coding workbook → analysis dataset (one row per record) |
| `review_stats.py` | The category rules shared by every analysis script |
| `manuscript_numbers.py` | Prints every statistic reported in the article |
| `make_results_tables.py` | Writes Tables 1–3 (characteristics, implementation and measurement practice, evidence map) |
| `make_supplementary_table.py`, `make_charting_fields_table.py` | Write the supplementary tables |
| `generate_figures.py` | Draws the figures |
| `rebuild_results.sh` | Runs the whole chain from one coding workbook |
| `prisma_identification.py` | Recomputes the identification stage (625 records → 195 duplicates → 430 → 11 book chapters → 419) from the raw database exports |

## Reproducing the results

The scripts need Python 3.10 or later with `openpyxl`. The figures also need `matplotlib`, `numpy` and `geopandas`; the world map downloads the Natural Earth country boundaries at run time.

```bash
# 1. compare the two coders and resolve the disagreements, then build the final workbook
python merge_coding.py compare --tr coding_TR.xlsx --ean coding_EAN.xlsx --ai coding_AI.xlsx --outdir out
python merge_coding.py apply   --tr coding_TR.xlsx --ean coding_EAN.xlsx --ai coding_AI.xlsx --outdir out
# 2. rebuild every number, table and figure from the final coding
./rebuild_results.sh out/coding_FINAL.xlsx results/
```

## Not included

- Full texts and abstracts of the screened papers, which remain under the publishers' copyright.
- The raw Scopus, Web of Science and ERIC exports, which are subject to the databases' licence terms. `prisma_identification.py` documents the deduplication and needs those exports to run.

## Licence

Code: MIT (see `LICENSE`). Data and documentation: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Citation

Rojas, T., Arias Navarro, E., & Jiménez Moya, E. (2026). *Video analysis as a pedagogical tool in physics education: a scoping review — data and code* [Data set and software]. https://github.com/tomas0821/video-analysis-scoping-review-data
