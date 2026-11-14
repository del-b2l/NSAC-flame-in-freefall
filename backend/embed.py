import json
import math
import os

import httpx
from dotenv import load_dotenv

from backend.data_loader import PROCESSED

load_dotenv()
BASE = "https://generativelanguage.googleapis.com/v1beta"
FILE = PROCESSED / "embeddings.json"


def embed(texts: list[str], task: str) -> list[list[float]] | None:
    key, model = os.getenv("GEMINI_API_KEY"), os.getenv("EMBED_MODEL")
    if not key or not model:
        print("[embed] GEMINI_API_KEY or EMBED_MODEL is not set")
        return None
    body = {"requests": [
        {"model": f"models/{model}", "content": {"parts": [{"text": t}]},
         "taskType": task, "outputDimensionality": 768}
        for t in texts]}
    try:
        r = httpx.post(f"{BASE}/models/{model}:batchEmbedContents",
                       headers={"x-goog-api-key": key}, json=body, timeout=60)
        if r.status_code != 200:
            print(f"[embed] {r.status_code}: {r.text[:300]}")
            return None
        return [e["values"] for e in r.json()["embeddings"]]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as e:
        print(f"[embed] request failed: {type(e).__name__}: {e}")
        return None


def _cos(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def search(question: str, k: int = 5) -> list[tuple[float, str]]:
    if not FILE.exists() or FILE.stat().st_size == 0:
        return []
    rows = json.loads(FILE.read_text(encoding="utf-8"))
    q = embed([question], "RETRIEVAL_QUERY")
    if not q:
        return []
    scored = sorted(((_cos(q[0], r["vector"]), r["id"]) for r in rows), reverse=True)[:k]
    print("[embed] top:", [(round(s, 3), i) for s, i in scored])
    return scored