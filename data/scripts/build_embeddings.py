import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.catalog import catalog, text_of
from backend.data_loader import PROCESSED
from backend.embed import embed

cat = catalog()
ids = list(cat)
texts = [text_of(cat[i]) for i in ids]
vectors = []
for i in range(0, len(texts), 50):
    v = embed(texts[i:i + 50], "RETRIEVAL_DOCUMENT")
    if v is None:
        sys.exit("Embedding failed, see the message above.")
    vectors += v
(PROCESSED / "embeddings.json").write_text(
    json.dumps([{"id": i, "vector": v} for i, v in zip(ids, vectors)]), encoding="utf-8")
print(len(ids), "documents embedded")