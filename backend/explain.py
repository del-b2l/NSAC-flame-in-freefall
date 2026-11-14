import json
import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from backend.data_loader import load_demo_answers, load_tests
from backend.verify import check_grounded

load_dotenv()
router = APIRouter()

# NUM = re.compile(r"\d+(?:\.\d+)?")

PROMPT = """You are summarising one NASA fire experiment record for a dashboard.

Rules:
- Use only the facts in the record below. Do not add outside knowledge.
- Write two plain-English sentences: what was tested, and what happened.
- Copy numbers exactly as written. Do not convert units, round, or calculate.
- Do not call anything safe or unsafe.
- If a field is null, do not mention it.

Record:
{record}
"""


# def _numbers(text: str) -> set[float]:
    # return {float(n) for n in NUM.findall(text)}


def _record_json(test) -> str:
    return json.dumps(test.model_dump(exclude={"source_url"}), ensure_ascii=False)


def _ask_gemini(record_json: str) -> str | None:
    key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")
    if not key or not model:
        print("[explain] GEMINI_API_KEY or GEMINI_MODEL is not set")
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [{"parts": [{"text": PROMPT.format(record=record_json)}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 400},
    }
    try:
        r = httpx.post(url, headers={"x-goog-api-key": key}, json=body,
               timeout=httpx.Timeout(60.0, connect=10.0))
        if r.status_code != 200:
            print(f"[explain] Gemini returned {r.status_code}: {r.text[:300]}")
            return None
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as e:
        print(f"[explain] request failed: {type(e).__name__}: {e}")
        return None


@router.post("/explain/{test_id}")
def explain(test_id: str):
    test = next((t for t in load_tests() if t.id == test_id), None)
    if test is None:
        raise HTTPException(status_code=404, detail=f"Unknown test: {test_id}")
    record = _record_json(test)
    src = {test_id: record}
    base = {"test_id": test_id, "source_url": test.source_url}

    text = _ask_gemini(record)
    if text:
        ok, why = check_grounded(text, src, implicit_source=test_id)
        if ok:
            return {**base, "text": text, "generated": True, "origin": "gemini"}
        print(f"[explain] rejected: {why}\n{text}")

    cached = load_demo_answers().get(test_id)
    if cached:
        ok, why = check_grounded(cached, src, implicit_source=test_id)
        if ok:
            return {**base, "text": cached, "generated": True, "origin": "cache"}
        print(f"[explain] cache for {test_id} rejected: {why}")

    return {**base, "text": test.result or "No summary available for this test.",
            "generated": False, "origin": "record"}