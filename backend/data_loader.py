import json
from pathlib import Path
from backend.models import TestRecord, Habitat

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
SAMPLE = ROOT / "data" / "sample"

def _read(*paths, default):
    for p in paths:
        if p.exists() and p.stat().st_size > 0:
            return json.loads(p.read_text(encoding="utf-8"))
    return default

def load_tests() -> list[TestRecord]:
    data = _read(PROCESSED / "tests.json", SAMPLE / "sample_tests.json", default=[])
    return [TestRecord(**t) for t in data]

def load_habitats() -> list[Habitat]:
    return [Habitat(**h) for h in _read(PROCESSED / "habitats.json", default=[])]

def load_safety() -> dict:
    return _read(PROCESSED / "safety.json", default={"materials": [], "rules": None})