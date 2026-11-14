# NSAC-flame-in-freefall
Team Tuesday Plan's submission for the NASA Space Apps Challenge 2026, Karachi.

# Flame in Freefall: Fire Safety Dashboard

## Run it
Backend: see backend/README (uvicorn backend.main:app --reload)
Frontend: cd frontend && npm install && npm run dev

## Data
The app reads `data/processed/tests.json`: 994 NASA tests, each with a source
link. It is generated, never edited by hand.

```bash
python data/scripts/fetch_psi.py    # NASA PSI tables -> data/raw/psi/ (gitignored)
python data/scripts/build_tests.py  # raw + curated Saffire -> data/processed/tests.json
```

See `data/raw/README.md` for what was fetched and `docs/ranking_rule.md` for how
the records are ranked.

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