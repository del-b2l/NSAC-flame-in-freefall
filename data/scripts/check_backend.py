import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient

from backend.data_loader import (
    PROCESSED,
    load_habitats,
    load_insights,
    load_safety,
    load_tests,
)
from backend.main import app

bad, warn = [], []


def read(name, default):
    p = PROCESSED / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() and p.stat().st_size else default


# --- tests.json ---
tests = load_tests()
ids = [t.id for t in tests]
by_id = {t.id: t for t in tests}
if len(ids) != len(set(ids)):
    bad.append("duplicate test ids")
if no_src := [t.id for t in tests if not t.source_url]:
    warn.append(f"{len(no_src)} tests have no source_url, e.g. {no_src[:3]}")
if out := [t.id for t in tests if (t.oxygen_pct is not None and not 0 <= t.oxygen_pct <= 100)
           or (t.pressure_psi is not None and not 0 <= t.pressure_psi <= 100)]:
    bad.append(f"oxygen or pressure out of range (units wrong?): {out[:5]}")
if fx := [i for i in ids if i.startswith("fixture-")]:
    warn.append(f"fixture records still in tests.json (remove before the demo): {fx}")
print(f"tests: {len(tests)}")

# --- safety.json must agree with tests.json ---
for m in load_safety().get("materials", []):
    for s in m.get("tests", []):
        t = by_id.get(s["test_id"])
        if t is None:
            bad.append(f"safety.json: {s['test_id']} not in tests.json")
        elif abs((s["oxygen_pct"] or 0) - (t.oxygen_pct or 0)) > 0.01 \
                or abs((s["pressure_psi"] or 0) - (t.pressure_psi or 0)) > 0.01:
            bad.append(f"safety.json disagrees with tests.json for {s['test_id']}")

# --- investigations and tags ---
invs = read("investigations.json", [])
inv_ids = [i.get("id") for i in invs]
if len(inv_ids) != len(set(inv_ids)):
    bad.append("duplicate investigation ids")
tags = read("investigation_tags.json", None)
if tags is None:
    warn.append("investigation_tags.json missing, so category tabs are empty")
else:
    tag_ids = {t["id"] for t in (tags if isinstance(tags, list) else [{"id": k} for k in tags])}
    if missing := tag_ids - set(inv_ids):
        bad.append(f"tag ids not in investigations.json: {sorted(missing)[:5]}")
    if untagged := set(inv_ids) - tag_ids:
        warn.append(f"{len(untagged)} investigations have no tag")
print(f"investigations: {len(invs)}")

# --- habitats, insights, demo answers ---
if len(load_habitats()) != 5:
    warn.append(f"expected 5 habitats, found {len(load_habitats())}")
ins = load_insights()
if not ins.get("key_finding"):
    bad.append("insights.json has no key_finding")
for sec in ("gaps", "earth_use"):
    for item in ins.get(sec, []):
        if not item.get("source_url"):
            bad.append(f"insights {sec}: item without source_url")
if stale := [k for k in read("demo_answers.json", {}) if k not in by_id]:
    bad.append(f"demo_answers.json has ids not in tests.json: {stale}")

# --- routes ---
client = TestClient(app)
for path in ["/health", "/habitats", "/tests", "/safety", "/safety/table",
             "/hardware", "/insights", "/investigations"]:
    r = client.get(path)
    if r.status_code != 200 or not r.json():
        bad.append(f"GET {path}: status {r.status_code} or empty body")
for h in load_habitats():
    r = client.post("/rank", json={"habitat": h.name})
    if r.status_code != 200 or not r.json():
        bad.append(f"POST /rank {h.name}: status {r.status_code} or empty")
    r = client.get("/brief", params={"habitat": h.name})
    if r.status_code != 200:
        bad.append(f"GET /brief {h.name}: status {r.status_code}")
        continue
    top = r.json().get("top_tests", [])
    if any(t["oxygen_pct"] is None or t["pressure_psi"] is None for t in top):
        bad.append(f"/brief {h.name}: contains a partially scored test")
    d = [t["distance"] for t in top]
    if d != sorted(d):
        bad.append(f"/brief {h.name}: not sorted by distance")
if client.post("/rank", json={"habitat": "Mars"}).status_code != 404:
    bad.append("POST /rank with an unknown habitat should return 404")
if client.get("/hardware").json().get("Not specified") and len(client.get("/hardware").json()) == 1:
    warn.append("/hardware: every investigation is 'Not specified' (hardware_family missing)")

print("\nPROBLEMS:" if bad else "\nNo problems.")
for b in bad:
    print("  x", b)
if warn:
    print("WARNINGS:")
    for w in warn:
        print("  -", w)
sys.exit(1 if bad else 0)