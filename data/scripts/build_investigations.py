#!/usr/bin/env python3
"""Build `data/processed/investigations.json` and `investigation_tags.json`.

Input: `data/raw/psi/manifest.json` and each `data/raw/psi/<ACCESSION>/_investigation.json`
(the metadata NASA's PSI page serves; run `fetch_psi.py` first).

An investigation is kept when NASA files it under the combustion research
area. Text fields (title, objective, hardware) are copied as NASA writes them.
`earth_benefits` is NASA's `researchImpacts` text, word for word: split into
one string per item when the whole text is a numbered list, else one string.
`hardware_family` is only set when the hardware text names one of the
facilities listed below. Nothing else is filled in.

Usage
-----
    python data/scripts/build_investigations.py            # write both files
    python data/scripts/build_investigations.py --check    # exit 1 if either is stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "psi"
MANIFEST = RAW / "manifest.json"
OUTPUT = ROOT / "data" / "processed" / "investigations.json"
TAGS_OUTPUT = ROOT / "data" / "processed" / "investigation_tags.json"

KEEP_RESEARCH_AREA = "Combustion Science"

# Phrase in NASA's experimentHardware text -> family name. First match wins,
# so the rack is checked before the apparatus that sits inside it.
HARDWARE_FAMILIES: tuple[tuple[str, str], ...] = (
    ("Combustion Integrated Rack", "Combustion Integrated Rack (CIR)"),
    ("Microgravity Science Glovebox", "Microgravity Science Glovebox (MSG)"),
    ("Cygnus", "Cygnus"),
)

# Grouping from the challenge page: what each program helps with.
CATEGORIES = ("prevent", "detect", "put out", "related")
CATEGORY_BY_ACRONYM: dict[str, str] = {
    "BASS": "prevent",
    "BASS-II": "prevent",
    "SAFFIRE-I": "prevent",
    "SAFFIRE-II": "prevent",
    "SAFFIRE-III": "prevent",
    "ACME BRE": "prevent",
    "SAME": "detect",
    "SAME-R": "detect",
    "DAFT / DAFT-2": "detect",
    "FLEX": "put out",
    "FLEX-2": "put out",
}

# Hand-written details from the first version of investigations.json, kept so
# a rebuild does not lose them. Every other investigation gets null here.
EXTRA_FIELDS = ("fuels", "sensors", "sample_size", "variables", "related_investigations")
CARRIED: dict[str, dict[str, Any]] = {
    "PSI-106": {
        "fuels": "Methane, ethylene, nitrogen-diluted mixtures",
        "sensors": "Flow rate and temperature sensors; high-resolution camera",
        "variables": "Burner diameter, coflow velocity, fuel composition",
        "related_investigations": [],
    },
    "PSI-159": {
        "fuels": "Propane, n-butane, n-pentane",
        "variables": "Reactant dilution, flow rate, pressure, flow direction",
        "related_investigations": [],
    },
    "PSI-10": {
        "variables": "Reactant dilution, flow rate, pressure, flow direction",
        "related_investigations": [],
    },
    "PSI-60": {
        "sensors": "Camera images analysed with color-ratio pyrometry",
        "related_investigations": ["SPICE"],
    },
    "PSI-62": {
        "sensors": "Two-color tomography of BASS and BASS-II imagery",
        "related_investigations": ["BASS", "BASS-II"],
    },
    "PSI-117": {
        "fuels": "n-alkane droplets",
        "related_investigations": ["FLEX"],
    },
}


def text_or_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


# "1. text", "1) text" or "(1) text" at the start of a line.
NUMBERED_ITEM = re.compile(r"^\s*(?:\((\d+)\)|(\d+)[.)])\s+(.*\S)\s*$")


def earth_benefits(impacts: object) -> list[str] | None:
    """NASA's research impacts as a list, without rewording anything.

    The text is only split when every non-empty line is a numbered item and
    the numbers run 1, 2, 3, ...; the numbering is removed and nothing else.
    Any other text (including a paragraph followed by a list) stays whole.
    """
    text = text_or_none(impacts)
    if text is None:
        return None
    lines = [line for line in text.splitlines() if line.strip()]
    items: list[str] = []
    for expected, line in enumerate(lines, start=1):
        match = NUMBERED_ITEM.match(line)
        if not match or int(match.group(1) or match.group(2)) != expected:
            return [text]
        items.append(match.group(3))
    return items if len(items) > 1 else [text]


def hardware_family(hardware: str | None) -> str | None:
    if not hardware:
        return None
    lowered = hardware.lower()
    for phrase, family in HARDWARE_FAMILIES:
        if phrase.lower() in lowered:
            return family
    return None


def accession_number(accession: str) -> int:
    return int(accession.split("-")[1])


def load_metadata() -> dict[str, dict]:
    """Every investigation in the manifest with its NASA metadata."""
    if not MANIFEST.exists():
        raise SystemExit("data/raw/psi/manifest.json is missing. Run: python data/scripts/fetch_psi.py")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["investigations"]
    metadata: dict[str, dict] = {}
    for accession in manifest:
        path = RAW / accession / "_investigation.json"
        if not path.exists():
            raise SystemExit(f"{path.relative_to(ROOT)} is missing. Run: python data/scripts/fetch_psi.py")
        metadata[accession] = json.loads(path.read_text(encoding="utf-8"))
    return metadata


def split_kept(metadata: dict[str, dict]) -> tuple[list[str], dict[str, str]]:
    """Return kept accessions (sorted) and a reason for each dropped one."""
    kept: list[str] = []
    dropped: dict[str, str] = {}
    for accession, meta in metadata.items():
        area = text_or_none(meta.get("researchArea"))
        if area == KEEP_RESEARCH_AREA:
            kept.append(accession)
        else:
            dropped[accession] = f"researchArea is {area!r}, not {KEEP_RESEARCH_AREA!r}"
    kept.sort(key=accession_number)
    return kept, dropped


def build_entry(accession: str, meta: dict, page: str) -> dict:
    hardware = text_or_none(meta.get("experimentHardware"))
    carried = CARRIED.get(accession, {})
    entry: dict[str, Any] = {
        "id": accession,
        "name": text_or_none(meta.get("title")),
        "acronym": text_or_none(meta.get("investigationAcronym")),
        "type": text_or_none(meta.get("projectType")),
        "doi": text_or_none(meta.get("doi")),
        "landing_url": page,
        "hardware": hardware,
        "hardware_family": hardware_family(hardware),
        "objective": text_or_none(meta.get("objective")),
        "earth_benefits": earth_benefits(meta.get("researchImpacts")),
    }
    for field in EXTRA_FIELDS:
        entry[field] = carried.get(field)
    return entry


def build_tag(entry: dict) -> dict:
    return {
        "id": entry["id"],
        "category": CATEGORY_BY_ACRONYM.get(entry["acronym"] or "", "related"),
    }


def build() -> tuple[list[dict], list[dict], dict[str, str]]:
    metadata = load_metadata()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["investigations"]
    kept, dropped = split_kept(metadata)
    entries = [build_entry(a, metadata[a], manifest[a]["page"]) for a in kept]
    tags = [build_tag(entry) for entry in entries]
    return entries, tags, dropped


def dump(payload: object) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if either output is out of date")
    args = parser.parse_args(argv)

    entries, tags, dropped = build()
    print(f"kept {len(entries)} combustion investigations, dropped {len(dropped)}")
    for accession, why in sorted(dropped.items(), key=lambda item: accession_number(item[0])):
        print(f"  dropped {accession}: {why}")

    outputs = ((OUTPUT, dump(entries)), (TAGS_OUTPUT, dump(tags)))
    if args.check:
        stale = [
            path for path, payload in outputs
            if (path.read_text(encoding="utf-8") if path.exists() else "") != payload
        ]
        for path in stale:
            print(f"{path.relative_to(ROOT)} is out of date; run build_investigations.py", file=sys.stderr)
        if stale:
            return 1
        print("investigations.json and investigation_tags.json are up to date")
        return 0

    for path, payload in outputs:
        path.write_text(payload, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
