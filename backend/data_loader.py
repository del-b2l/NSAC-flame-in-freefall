import json
from pathlib import Path
from backend.models import TestRecord

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "processed" / "sample_tests.json"

def load_tests() -> list[TestRecord]:
    with open(DATA_FILE, encoding="utf-8") as f:
        return [TestRecord(**item) for item in json.load(f)]