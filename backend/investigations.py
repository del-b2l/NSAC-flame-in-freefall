import json
from typing import Optional

from fastapi import APIRouter

from backend.data_loader import PROCESSED

router = APIRouter()


def _load(name: str, default):
    p = PROCESSED / name
    if p.exists() and p.stat().st_size > 0:
        return json.loads(p.read_text(encoding="utf-8"))
    return default


@router.get("/investigations")
def investigations(category: Optional[str] = None):
    items = _load("investigations.json", [])
    tags = _load("investigation_tags.json", [])
    if isinstance(tags, dict):
        tags = [{"id": k, **v} for k, v in tags.items()]
    by_id = {t["id"]: t for t in tags if "id" in t}

    merged = []
    for inv in items:
        tag = by_id.get(inv.get("id"), {})
        merged.append({
            **inv,
            "category": tag.get("category"),
        })

    if category:
        merged = [m for m in merged if (m["category"] or "").lower() == category.lower()]
    return merged