#!/usr/bin/env python3
"""Download NASA PSI combustion experimental tables into `data/raw/psi/`.

Why this file exists: NASA's Physical Science Informatics (PSI) database is the
source the challenge links to, but its file download needs a browser session.
The download endpoint below works without one. This script fetches the raw
files unchanged and records where each came from, so every number in
`data/processed/tests.json` can be traced back to a NASA file.

Nothing here is edited after download. `data/scripts/build_tests.py` does the
reading and the unit conversion.

Usage
-----
    python data/scripts/fetch_psi.py                 # every combustion investigation
    python data/scripts/fetch_psi.py --only PSI-159 PSI-69
    python data/scripts/fetch_psi.py --force         # re-download existing files
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://psi.nasa.gov"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "raw" / "psi"
MANIFEST = OUT / "manifest.json"

SEARCH_URL = f"{BASE}/geode-py/ws/repo/search?term=combustion&source=psi&type=investigation&size=50"
HEADERS = {"User-Agent": "flame-in-freefall/1.0 (Space Apps 2026; data provenance)"}
PAUSE_SECONDS = 0.4
RETRIES = 3


def _get(url: str, timeout: int = 60) -> bytes:
    """GET with retries. PSI occasionally drops the first connection."""
    last: Exception | None = None
    for attempt in range(RETRIES):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"could not fetch {url}: {last}")


def combustion_accessions() -> list[str]:
    payload = json.loads(_get(SEARCH_URL))
    return [hit["_source"]["Accession"] for hit in payload["hits"]["hits"]]


def investigation(accession: str) -> dict:
    return json.loads(_get(f"{BASE}/geode-py/ws/repo/investigations/{accession}"))


def table_url(accession: str, file_name: str, version: int) -> str:
    query = urllib.parse.urlencode(
        {"file": file_name, "version": version, "redirect": False}
    )
    return f"{BASE}/geode-py/ws/studies/{accession}/download?{query}"


def download_table(accession: str, table: dict) -> bytes:
    """The endpoint answers either with the CSV itself or with a signed S3 URL."""
    body = _get(table_url(accession, table["file_name"], table.get("version", 1)))
    if body[:4] == b"http":
        body = _get(body.decode("utf-8").strip())
    return body


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"generated_by": "data/scripts/fetch_psi.py", "investigations": {}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", nargs="+", metavar="ACCESSION", help="limit to these accessions")
    parser.add_argument("--force", action="store_true", help="re-download files that already exist")
    args = parser.parse_args(argv)

    OUT.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    wanted = args.only or combustion_accessions()
    downloaded = skipped = failed = 0

    for accession in wanted:
        try:
            record = investigation(accession)
        except Exception as exc:  # noqa: BLE001 - report and keep going
            print(f"[{accession}] metadata failed: {exc}", file=sys.stderr)
            failed += 1
            continue

        folder = OUT / accession
        folder.mkdir(exist_ok=True)
        (folder / "_investigation.json").write_text(
            json.dumps(record, indent=1, sort_keys=True), encoding="utf-8"
        )

        tables = record.get("experimentalTable") or []
        entry = {
            "acronym": record.get("investigationAcronym"),
            "title": record.get("title"),
            "doi": record.get("doi"),
            "page": f"{BASE}/physci/repo/data/investigations/{accession}",
            "tables": [],
        }

        for table in tables:
            name = table["file_name"]
            path = folder / name
            entry["tables"].append(
                {
                    "file": name,
                    "version": table.get("version", 1),
                    "download_url": table_url(accession, name, table.get("version", 1)),
                    "bytes": table.get("file_size"),
                }
            )
            if path.exists() and not args.force:
                skipped += 1
                continue
            try:
                data = download_table(accession, table)
            except Exception as exc:  # noqa: BLE001
                print(f"[{accession}] {name}: {exc}", file=sys.stderr)
                failed += 1
                continue
            path.write_bytes(data)
            entry["tables"][-1].update({"bytes": len(data), "sha256": sha256(data)})
            downloaded += 1
            time.sleep(PAUSE_SECONDS)

        entry["fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        manifest["investigations"][accession] = entry
        print(f"[{accession}] {record.get('investigationAcronym') or '?':<14} "
              f"{len(tables)} table(s)")

    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
    print(f"\ndownloaded {downloaded}, already present {skipped}, failed {failed}")
    print(f"manifest: {MANIFEST.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
