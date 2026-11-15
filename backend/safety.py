from fastapi import APIRouter

from backend.data_loader import load_habitats, load_investigations, load_safety

router = APIRouter()

# A nearest test whose oxygen is further than this from the habitat's is not
# counted as a test of that habitat. The limit is the team's choice, not a
# NASA value; the nearest test is still returned so the page can cite it.
OXYGEN_CUTOFF_POINTS = 10.0


def _gaps(test: dict, hab):
    o, p = test.get("oxygen_pct"), test.get("pressure_psi")
    if o is None or p is None:
        return None
    return abs(o - hab.oxygen_pct), abs(p - hab.pressure_psi)


@router.get("/safety/table")
def safety_table():
    safety = load_safety()
    habitats = load_habitats()
    rules = safety.get("rules") or {}
    rows = []
    for m in safety.get("materials", []):
        cells = []
        for h in habitats:
            best = None
            for t in m.get("tests", []):
                if t.get("oxygen_pct") is None or t.get("pressure_psi") is None:
                    continue
                og = abs(t["oxygen_pct"] - h.oxygen_pct)
                pg = abs(t["pressure_psi"] - h.pressure_psi)
                if best is None or og + pg < best[0]:
                    best = (og + pg, og, pg, t)
            cell = {"habitat": h.name}
            if m["material"] in rules:
                cell |= {"state": "rule", "rule": rules[m["material"]]}
            elif best:
                d, og, pg, t = best
                state = "tested" if og <= OXYGEN_CUTOFF_POINTS else "missing"
                cell |= {"state": state, "nearest_test": t,
                         "oxygen_gap": round(og, 2), "pressure_gap": round(pg, 2),
                         "distance": round(d, 2)}
            else:
                cell |= {"state": "missing", "nearest_test": None}
            cells.append(cell)
        rows.append({"material": m["material"], "cells": cells})
    return {"habitats": [h.name for h in habitats], "rows": rows,
            "rules_read": bool(rules),
            "oxygen_cutoff_points": OXYGEN_CUTOFF_POINTS,
            "standard_rule": safety.get("standard_rule")}


@router.get("/hardware")
def hardware():
    groups: dict[str, list] = {}
    for inv in load_investigations():
        family = inv.get("hardware_family") or "Not specified"
        groups.setdefault(family, []).append({"id": inv["id"], "name": inv["name"]})
    return groups