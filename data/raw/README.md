# Raw data

Files here are copied from NASA exactly as they publish them. **Never edit a
file in this folder.** If a number is wrong, fix it in the build step or raise
it with a source, never by hand-editing a raw file.

Only `README.md` and `psi/manifest.json` are committed. The downloaded CSVs are
excluded by `.gitignore` (24 MB) and can be re-fetched by anyone:

```bash
python data/scripts/fetch_psi.py
```

## What is here

| Folder | What it is | Where it came from |
|---|---|---|
| `psi/<ACCESSION>/` | The "Experimental table" CSV that NASA publishes for one investigation, plus `_investigation.json` (its metadata) | `https://psi.nasa.gov/physci/repo/data/investigations/<ACCESSION>` |
| `psi/manifest.json` | Every file's name, version, download URL, size and SHA-256 | written by `data/scripts/fetch_psi.py` |

The PSI page's own download button needs a browser session. The script uses the
endpoint that button calls,
`/geode-py/ws/studies/<ACCESSION>/download?file=<name>&version=<n>&redirect=false`,
which answers either with the CSV or with a signed S3 link.

## Which tables we actually use

Only investigations whose table has **both** an oxygen and a pressure column
can produce a record that matches `docs/data_schema.md`. As of Saturday
14 November 2026:

| Accession | Investigation | Rows | Oxygen column | Pressure column |
|---|---|---|---|---|
| PSI-159 | CFI-G | 179 | `XO2 before test` (mole fraction) | `approx p` (bar) |
| PSI-10 | ACME / Flame Design | 187 | `XO2 (init)` (mole fraction) | `pmean` (atm) |
| PSI-69 | FLEX | 274 | `O initial ambient composition` (mole fraction) | `Ambient pressure` (mmHg) |
| PSI-39 | CFI | 87 | `Oxygen` (mole fraction) | `Pressure` (text, e.g. `1 atm`) |

The fire-safety investigations (Saffire I–III, BASS, BASS-II) publish oxygen
and airflow but **no pressure**, so they cannot fill a record on their own.
Saffire IV–VI are not in PSI at all; they come from the 2024 NTRS paper and are
kept in `data/sample/sample_tests.json`.

## Adding a source

1. Add it to `data/scripts/fetch_psi.py` (or run it with `--only ACCESSION`).
2. Add the column map and unit conversion in `data/scripts/build_tests.py`.
3. Add a test in `data/tests/test_build.py` pinned to one known row.
4. Note the column names and units in the table above.

## Log

| Date | Who | What |
|---|---|---|
| 2026-11-14 | Shaheer | Created this file. Fetched 25 experimental tables from 26 combustion investigations with `fetch_psi.py`; manifest records the versions and hashes. |
