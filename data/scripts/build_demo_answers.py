import json
from pathlib import Path
import httpx

OUT = Path(__file__).resolve().parent.parent / "processed" / "demo_answers.json"
IDS = ["saffire-vi-3", "saffire-vi-4", "saffire-v-2"]

answers = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() and OUT.stat().st_size else {}

for tid in IDS:
    r = httpx.post(f"http://localhost:8000/explain/{tid}", timeout=60)
    data = r.json()
    if data.get("origin") == "gemini":
        answers[tid] = data["text"]
        print("saved", tid)
    else:
        print("skipped", tid, "->", data.get("origin"))

OUT.write_text(json.dumps(answers, indent=2, ensure_ascii=False), encoding="utf-8")