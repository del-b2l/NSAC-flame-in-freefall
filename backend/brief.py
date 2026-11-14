from fastapi import APIRouter, HTTPException

from backend.data_loader import load_habitats, load_insights, load_tests
from backend.ranking import rank_tests_by_tier

router = APIRouter()


def _as_dict(t):
    return t.model_dump() if hasattr(t, "model_dump") else dict(t)


@router.get("/brief")
def brief(habitat: str):
    hab = next((h for h in load_habitats() if h.name == habitat), None)
    if hab is None:
        raise HTTPException(status_code=404, detail=f"Unknown habitat: {habitat}")

    ranked = rank_tests_by_tier(load_tests(), hab)

    # Exclude Tier 3, but include both Tier 1 and Tier 2.
    scored = [
        r for r in ranked
        if r["tier"] != 3
    ][:5]

    top_tests = []

    for r in scored:
        t = r["test"]

        top_tests.append({
            "id": t.id,
            "investigation": t.investigation,
            "material": t.material,
            "oxygen_pct": t.oxygen_pct,
            "pressure_psi": t.pressure_psi,
            "distance": r["distance"],
            "tier": r["tier"],
            "scored_on": r["scored_on"],
            "label": r["label"],
            "source_url": t.source_url,
        })

    ins = load_insights()
    return {
        "habitat": {"name": hab.name, "oxygen_pct": hab.oxygen_pct,
                    "pressure_psi": hab.pressure_psi, "status": hab.status},
        "top_tests": top_tests,
        "key_finding": ins.get("key_finding"),
        "gap": (ins.get("gaps") or [None])[0],
        "control_need": ins.get("control_need"),
    }