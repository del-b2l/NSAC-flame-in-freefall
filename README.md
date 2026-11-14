# NSAC-flame-in-freefall
Team Tuesday Plan's submission for the NASA Space Apps Challenge 2026, Karachi.

# Flame in Freefall: Fire Safety Dashboard

## Run it
Backend: see backend/README (uvicorn backend.main:app --reload)
Frontend: cd frontend && npm install && npm run dev

## Data
The app reads `data/processed/tests.json`: 986 NASA tests, each with a source
link. It is generated, never edited by hand.

```bash
python data/scripts/fetch_psi.py             # NASA PSI tables + metadata -> data/raw/psi/ (gitignored)
python data/scripts/build_tests.py           # raw + curated Saffire -> data/processed/tests.json
python data/scripts/build_investigations.py  # PSI metadata -> data/processed/investigations.json, investigation_tags.json
python data/scripts/build_report.py          # processed files -> docs/data_report.md
```

Each build script also takes `--check`, which exits with an error if its output
is out of date.

See `data/raw/README.md` for what was fetched, `docs/data_report.md` for the
per-investigation numbers, and `docs/ranking_rule.md` for how the records are
ranked.

## Tests
```bash
python -m pytest backend/tests data/tests -q
```

## Team
- Batool: lead, backend core, RAG later
- Ayesh: data pipeline
- Shaheer: ranking logic
- Muntaha: React dashboard
- Anumta: HTML/CSS pages, slides, docs

## Docs
See docs/ for the data schema, sources, and architecture.