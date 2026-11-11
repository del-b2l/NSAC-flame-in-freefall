from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.data_loader import load_tests
from backend.models import Habitat
from backend.ranking import rank_tests

app = FastAPI(title="Flame in Freefall API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tests")
def get_tests():
    return load_tests()

@app.post("/rank")
def rank(habitat: Habitat):
    return rank_tests(load_tests(), habitat)