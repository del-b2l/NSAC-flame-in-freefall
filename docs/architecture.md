# Architecture

## The pieces

```
Raw NASA files (data/raw/)
        |
        |  data/scripts/build_tests.py  (Ayesh)
        v
Processed JSON (data/processed/)
   tests.json, habitats.json
        |
        |  backend/data_loader.py  (Batool)
        v
Backend API (FastAPI, backend/main.py)
   GET  /health   -> status check
   GET  /tests    -> all test records
   POST /rank     -> tests sorted for a chosen habitat
        |
        |  browser requests (JSON)
        v
Frontend (React, frontend/src/)
   HabitatPicker.tsx  -> user picks a habitat, sends it to /rank
   TestList.tsx       -> shows the sorted tests
   SafetyTable.tsx    -> shows the honest safety table
   App.tsx            -> puts the screens together
```

## Who owns what

| Layer | Owner | Files |
|---|---|---|
| Raw files | Ayesh | `data/raw/` |
| Cleaning script | Ayesh | `data/scripts/build_tests.py` |
| Backend routes and data loading | Batool | `backend/main.py`, `backend/data_loader.py`, `backend/models.py` |
| Ranking | Shaheer | `backend/ranking.py`, `backend/tests/test_ranking.py` |
| Screens | Muntaha | `frontend/src/components/HabitatPicker.tsx`, `TestList.tsx`, `App.tsx` |
| Safety table | Batool (with Muntaha) | `frontend/src/components/SafetyTable.tsx` |
| Styling and content | Anumta | `frontend/src/App.css`, the three tabs |

## Rules that keep it simple

- The frontend never reads files directly. It only calls the backend.
- The backend never edits the data. It only reads `data/processed/`.
- Every record must match `docs/data_schema.md`. If you change one, change the other in the same pull request.
- Ranking happens in the backend, not in the browser, so every user sees the same order.

## Later (not for the hackathon)

`rag/` will hold a search feature that finds the most relevant records for a question. It reads the same processed data and does not change it.