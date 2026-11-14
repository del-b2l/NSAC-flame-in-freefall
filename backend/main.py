from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.data_loader import load_tests, load_habitats, load_safety
from backend.models import RankRequest
from backend.ranking import rank_tests

app = FastAPI(title="Flame in Freefall API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/habitats")
def habitats():
    return load_habitats()

@app.get("/tests")
def tests():
    return load_tests()

@app.post("/rank")
def rank(req: RankRequest):
    habitat = next((h for h in load_habitats() if h.name == req.habitat), None)
    if habitat is None:
        raise HTTPException(status_code=404, detail=f"Unknown habitat: {req.habitat}")
    return rank_tests(load_tests(), habitat)

@app.get("/safety")
def safety():
    return load_safety()

# After Shaheer's PR is merged:
# from backend.investigations import router as investigations_router
# app.include_router(investigations_router)