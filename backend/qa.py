import json
import os
import re

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.catalog import catalog
from backend.data_loader import load_habitats, load_insights, load_tests, read_processed
from backend.embed import search
from backend.ranking import rank_tests

load_dotenv()
router = APIRouter()

STOP = {"the", "and", "for", "are", "was", "were", "what", "which", "how", "does", "did", "with", "from", "that", "this", "can", "who", "when", "where", "why", "you", "flame", "flames", "fire", "test", "tests", "experiment", "experiments", "combustion"}
CITE = re.compile(r"\[([^\[\]]+)\]")
NUM = re.compile(r"\d+(?:\.\d+)?")
REFUSAL = "I can't answer that from the records."

PROMPT = """You answer questions about NASA microgravity fire experiments using ONLY the records below.

Rules:
- Use only facts in the records. No outside knowledge.
- Answer in one to three plain sentences, no lists.
- After every claim, cite the record id in square brackets, like [saffire-vi-3]. Cite only ids that appear below.
- Copy numbers exactly as written. Do not convert, round or calculate.
- Do not say anything is safe or unsafe.
- If the records do not contain the answer, reply exactly: {refusal}

Question: {question}

Records:
{records}
"""


class QARequest(BaseModel):
    question: str
    habitat: str | None = None


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in STOP}


def _numbers(text: str) -> set[float]:
    text = re.sub(r"(?<=\d),(?=\d{3})", "", text)
    return {float(n) for n in NUM.findall(text)}


def _norm(q: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", q.lower()))


def _add_test(ctx: dict, d: dict) -> None:
    rec = {k: d[k] for k in ("investigation", "material", "oxygen_pct", "pressure_psi", "airflow", "result")
           if d.get(k) is not None}
    if d.get("conditions"):
        rec["conditions"] = dict(list(d["conditions"].items())[:10])
    ctx[d["id"]] = {"kind": "test", "label": f"{d['investigation']} ({d['id']})",
                    "source_url": d.get("source_url"), "record": rec}


def _ranked(habitat: str, n: int = 5) -> list[dict]:
    hab = next((h for h in load_habitats() if h.name.lower() == habitat.lower()), None)
    if hab is None:
        return []
    out = []
    for r in rank_tests(load_tests(), hab):
        t = r["test"] if isinstance(r, dict) and "test" in r else r
        t = t.model_dump() if hasattr(t, "model_dump") else dict(t)
        if t.get("oxygen_pct") is not None and t.get("pressure_psi") is not None:
            out.append(t)
        if len(out) == n:
            break
    return out


def _build_context(question: str, habitat: str | None) -> dict:
    q = _tokens(question)
    ctx: dict = {}

    # investigations
    scored = []
    for inv in read_processed("investigations.json", []):
        rec = {k: v for k, v in inv.items() if v not in (None, "", [])}
        s = len(q & _tokens(" ".join(str(v) for v in rec.values())))
        if s:
            scored.append((-s, inv["id"], inv, rec))
    for _, iid, inv, rec in sorted(scored, key=lambda x: (x[0], x[1]))[:5]:
        ctx[iid] = {"kind": "investigation", "label": inv.get("name", iid),
                    "source_url": inv.get("landing_url"), "record": rec}

    # tests
    tscored = []
    for t in load_tests():
        d = t.model_dump()
        text = " ".join(str(v) for v in d.values() if v is not None and not isinstance(v, dict))
        text += " " + " ".join(f"{k} {v}" for k, v in d["conditions"].items())
        s = len(q & _tokens(text))
        if s:
            tscored.append((-s, d["id"], d))
    for _, _, d in sorted(tscored, key=lambda x: (x[0], x[1]))[:6]:
        _add_test(ctx, d)

    # habitat and its closest tests
    name = habitat or next((h.name for h in load_habitats() if h.name.lower() in question.lower()), None)
    hab = next((h for h in load_habitats() if name and h.name.lower() == name.lower()), None)
    if hab:
        ctx["habitat-" + _norm(hab.name).replace(" ", "-")] = {
            "kind": "habitat", "label": f"{hab.name} reference conditions", "source_url": hab.source_url,
            "record": {"name": hab.name, "oxygen_pct": hab.oxygen_pct, "pressure_psi": hab.pressure_psi,
                       "status": hab.status}}
        for d in _ranked(hab.name):
            _add_test(ctx, d)

    # insights and Earth-use items
    ins = load_insights()
    items = []
    if ins.get("key_finding"):
        items.append(("key-finding", ins["key_finding"]))
    items += [(f"gap-{i}", g) for i, g in enumerate(ins.get("gaps", []), 1)]
    items += [(f"earth-{i}", e) for i, e in enumerate(read_processed("earth_use.json", []), 1)]
    for iid, it in items:
        if q & _tokens(f"{it.get('title', '')} {it.get('text', '')}"):
            ctx[iid] = {"kind": "insight", "label": it.get("title") or it.get("source_label", iid),
                        "source_url": it.get("source_url"),
                        "record": {k: it[k] for k in ("title", "text", "status") if it.get(k)}}
    cat = catalog()
    for _score, iid in search(question):
        if iid in cat:
            ctx.setdefault(iid, cat[iid])
    return ctx


def _generate(prompt: str) -> str | None:
    key, model = os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_MODEL")
    if not key or not model:
        print("[qa] GEMINI_API_KEY or GEMINI_MODEL is not set")
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500}}
    try:
        r = httpx.post(url, headers={"x-goog-api-key": key}, json=body,
                       timeout=httpx.Timeout(60.0, connect=10.0))
        if r.status_code != 200:
            print(f"[qa] Gemini returned {r.status_code}: {r.text[:300]}")
            return None
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as e:
        print(f"[qa] request failed: {type(e).__name__}: {e}")
        return None


def _verify(answer: str, ctx: dict, question: str) -> tuple[bool, str]:
    cited = [c.strip() for grp in CITE.findall(answer) for c in grp.split(",")]
    if not cited:
        return False, "no citations"
    if unknown := [c for c in cited if c not in ctx]:
        return False, f"unknown ids {unknown}"
    allowed = _numbers(question)
    for c in set(cited):
        allowed |= _numbers(json.dumps(ctx[c]["record"], ensure_ascii=False))
    if extra := _numbers(CITE.sub("", answer)) - allowed:
        return False, f"numbers not in cited records: {sorted(extra)}"
    return True, ""


def _cards(ctx: dict, ids=None) -> list[dict]:
    return [{"id": k, "kind": v["kind"], "label": v["label"], "source_url": v["source_url"]}
            for k, v in ctx.items() if ids is None or k in ids]


@router.post("/qa")
def qa(req: QARequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question is empty")
    ctx = _build_context(question, req.habitat)
    base = {"question": question, "answer": None, "verified": False, "origin": "none",
            "citations": [], "sources_considered": _cards(ctx)}
    if not ctx:
        return {**base, "note": "No matching records."}

    prompt = PROMPT.format(refusal=REFUSAL, question=question,
                           records="\n".join(json.dumps({"id": k, **v["record"]}, ensure_ascii=False)
                                             for k, v in ctx.items()))
    candidates = []
    if live := _generate(prompt):
        candidates.append(("gemini", live))
    for row in read_processed("demo_qa.json", []):
        if _norm(row["question"]) == _norm(question):
            candidates.append(("cache", row["answer"]))

    for origin, text in candidates:
        text = text.strip()
        if text == REFUSAL:
            return {**base, "verified": True, "origin": origin, "note": "The records don't answer this."}
        ok, why = _verify(text, ctx, question)
        if ok:
            ids = list(dict.fromkeys(c.strip() for g in CITE.findall(text) for c in g.split(",")))
            return {**base, "answer": text, "verified": True, "origin": origin, "citations": _cards(ctx, ids)}
        print(f"[qa] rejected ({origin}): {why}\n{text}")
    return {**base, "note": "Couldn't produce a verified answer. These are the closest records."}


@router.get("/qa/examples")
def examples():
    return [row["question"] for row in read_processed("demo_qa.json", [])]