from backend.data_loader import load_insights, read_processed


def catalog() -> dict:
    cat = {}
    for inv in read_processed("investigations.json", []):
        rec = {k: v for k, v in inv.items() if v not in (None, "", [])}
        cat[inv["id"]] = {"kind": "investigation", "label": inv.get("name", inv["id"]),
                          "source_url": inv.get("landing_url"), "record": rec}
    ins = load_insights()
    items = []
    if ins.get("key_finding"):
        items.append(("key-finding", ins["key_finding"]))
    items += [(f"gap-{i}", g) for i, g in enumerate(ins.get("gaps", []), 1)]
    items += [(f"earth-{i}", e) for i, e in enumerate(read_processed("earth_use.json", []), 1)]
    for iid, it in items:
        cat[iid] = {"kind": "insight", "label": it.get("title") or it.get("source_label", iid),
                    "source_url": it.get("source_url"),
                    "record": {k: it[k] for k in ("title", "text", "status") if it.get(k)}}
    return cat


def text_of(entry: dict) -> str:
    return f"{entry['label']}. " + " ".join(f"{k}: {v}" for k, v in entry["record"].items())