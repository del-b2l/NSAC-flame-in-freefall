from fastapi import APIRouter

from backend.data_loader import load_habitats, load_investigations, load_safety

router = APIRouter()


def _gaps(test: dict, hab):
    o, p = test.get("oxygen_pct"), test.get("pressure_psi")
    if o is None or p is None:
        return None
    return abs(o - hab.oxygen_pct), abs(p - hab.pressure_psi)


@router.get("/safety/table")
def safety_table():
    safety = load_safety()
    habitats = load_habitats()
    rows = []
    for m in safety.get("materials", []):
        cells = []
        for h in habitats:
            best = None
            for t in m.get("tests", []):
                g = _gaps(t, h)
                if g is None:
                    continue
                d = g[0] + g[1]
                if best is None or d < best[0]:
                    best = (d, g, t)
            if best is None:
                cells.append({"habitat": h.name, "nearest_test": None})
            else:
                d, (og, pg), t = best
                cells.append({
                    "habitat": h.name,
                    "nearest_test": t,
                    "oxygen_gap": round(og, 2),
                    "pressure_gap": round(pg, 2),
                    "distance": round(d, 2),
                })
        rows.append({"material": m["material"], "cells": cells})
    return {
        "habitats": [h.name for h in habitats],
        "rows": rows,
        "rules": safety.get("rules"),
        "rules_note": safety.get("rules_note"),
    }

@router.get("/hardware")
def hardware():
    groups: dict[str, list] = {}
    for inv in load_investigations():
        family = inv.get("hardware_family") or "Not specified"
        groups.setdefault(family, []).append({"id": inv["id"], "name": inv["name"]})
    return groups