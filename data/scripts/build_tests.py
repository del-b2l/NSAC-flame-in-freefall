#!/usr/bin/env python3
"""Build `data/processed/tests.json` from the raw NASA files.

Inputs, in order:

1. `data/sample/sample_tests.json` — Saffire IV-VI, transcribed by hand from
   the 2024 NTRS paper because those runs are not in PSI.
2. The PSI experimental tables in `data/raw/psi/<ACCESSION>/` (run
   `fetch_psi.py` first).

Everything else is generated. A row is only kept when it has a numeric oxygen
value, a numeric pressure that survives a sanity range, and a `source_url`.
Rows that fail are counted and reported; nothing is guessed.

Units: oxygen is always mol %, pressure is always psi. Each source declares the
unit it publishes and the converter below does the arithmetic.

Usage
-----
    python data/scripts/build_tests.py            # write tests.json
    python data/scripts/build_tests.py --dry-run  # report only
    python data/scripts/build_tests.py --check    # exit 1 if tests.json is stale
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "psi"
MANIFEST = RAW / "manifest.json"
CURATED = ROOT / "data" / "sample" / "sample_tests.json"
OUTPUT = ROOT / "data" / "processed" / "tests.json"

# psi per unit. Values from NIST SP 811 appendix B.
PSI_PER: dict[str, float] = {
    "psi": 1.0,
    "atm": 14.695_948_8,
    "bar": 14.503_773_8,
    "kpa": 0.145_037_738,
    "mmhg": 0.019_336_778,  # 1 mmHg = 1 torr
    "torr": 0.019_336_778,
    "pa": 0.000_145_037_738,
}

OXYGEN_RANGE = (1.0, 100.0)  # mol %
PRESSURE_RANGE = (0.5, 100.0)  # psi


@dataclass(frozen=True)
class Source:
    """One CSV table and the columns in it we know how to read."""

    accession: str
    table: str
    prefix: str
    id_col: str
    oxygen_col: str
    oxygen_scale: float  # multiply the raw value by this to get mol %
    pressure_col: str
    pressure_unit: str
    material_col: str | None = None


SOURCES: tuple[Source, ...] = (
    Source(
        accession="PSI-159",
        table="PSI-159_Experimental table_CFI-G_Normal Flames.csv",
        prefix="cfig-normal",
        id_col="Test",
        oxygen_col="XO2 before test",
        oxygen_scale=100.0,
        pressure_col="approx p (bar)",
        pressure_unit="bar",
        material_col="Fuel",
    ),
    Source(
        accession="PSI-159",
        table="PSI-159_Experimental table_CFI-G_Inverse Flames.csv",
        prefix="cfig-inverse",
        id_col="Test",
        oxygen_col="XO2",
        oxygen_scale=100.0,
        pressure_col="approx p (bar)",
        pressure_unit="bar",
        material_col="Fuel",
    ),
    Source(
        accession="PSI-10",
        table="PSI-10_Experimental table_Flame Design_Normal Flame.csv",
        prefix="acme-fd-normal",
        id_col="Test",
        oxygen_col="XO2 (init)",
        oxygen_scale=100.0,
        pressure_col="pmean (atm)",
        pressure_unit="atm",
        material_col="Fuel",
    ),
    Source(
        accession="PSI-10",
        table="PSI-10_Experimental table_Flame Design_Inverse Flame.csv",
        prefix="acme-fd-inverse",
        id_col="Test",
        oxygen_col="XO2",
        oxygen_scale=100.0,
        pressure_col="pmean (atm)",
        pressure_unit="atm",
        material_col="Fuel",
    ),
    Source(
        accession="PSI-69",
        table="PSI-69_Experimental table_FLEX.csv",
        prefix="flex",
        id_col="FLEX Identifier",
        oxygen_col="O initial ambient composition; mole fraction",
        oxygen_scale=100.0,
        pressure_col="Ambient pressure; mmHg",
        pressure_unit="mmHg",
        material_col="Fuel",
    ),
    Source(
        accession="PSI-39",
        table="PSI-39_Experimental table_CFI.csv",
        prefix="cfi",
        id_col="Flex Number",
        oxygen_col="Oxygen",
        oxygen_scale=100.0,
        pressure_col="Pressure",
        pressure_unit="atm",
        material_col="Fuel",
    ),
)


# --- units -----------------------------------------------------------------


def to_psi(value: float, unit: str) -> float:
    """Convert a pressure to psi. Raises for a unit we do not know."""
    key = unit.strip().lower()
    if key not in PSI_PER:
        raise ValueError(f"unknown pressure unit: {unit!r}")
    return value * PSI_PER[key]


def parse_number(text: object) -> float | None:
    """Read a plain number, tolerating stray spaces and a trailing percent sign."""
    if text is None:
        return None
    cleaned = str(text).strip().replace("%", "").replace(",", "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_pressure(text: object, default_unit: str) -> float | None:
    """Read `1.02`, or `1 atm`, or `13.8 psi`, and return psi."""
    if text is None:
        return None
    raw = str(text).strip()
    if not raw:
        return None
    match = re.fullmatch(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*([A-Za-z/]+)?", raw)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2) or default_unit
    return to_psi(value, unit)


def normalise_key(key: object) -> str:
    """Collapse the uneven header spacing NASA ships (`" XO2  after test"`)."""
    return " ".join(str(key).strip().split())


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


# --- building --------------------------------------------------------------


def read_table(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    reader = csv.DictReader(text.splitlines())
    return [
        {normalise_key(k): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k}
        for row in reader
    ]


def build_record(source: Source, row: dict[str, str], investigation: str, page: str) -> tuple[dict | None, str]:
    """Turn one CSV row into a schema record, or explain why it cannot be one."""
    oxygen = parse_number(row.get(source.oxygen_col))
    pressure = parse_pressure(row.get(source.pressure_col), source.pressure_unit)
    if oxygen is None:
        return None, "no oxygen"
    if pressure is None:
        return None, "no pressure"

    oxygen_pct = round(oxygen * source.oxygen_scale, 2)
    pressure_psi = round(pressure, 2)
    if not OXYGEN_RANGE[0] <= oxygen_pct <= OXYGEN_RANGE[1]:
        return None, f"oxygen out of range ({oxygen_pct})"
    if not PRESSURE_RANGE[0] <= pressure_psi <= PRESSURE_RANGE[1]:
        return None, f"pressure out of range ({pressure_psi})"

    test_id = row.get(source.id_col) or ""
    material = row.get(source.material_col) if source.material_col else None
    return (
        {
            "id": slug(f"{source.prefix}-{test_id}") if test_id else "",
            "investigation": investigation,
            "material": material or None,
            "oxygen_pct": oxygen_pct,
            "pressure_psi": pressure_psi,
            "airflow": None,
            "result": None,
            "conditions": {**row, "Accession": source.accession, "Table": source.table},
            "source_url": page,
        },
        "",
    )


def load_manifest() -> dict:
    if not MANIFEST.exists():
        raise SystemExit(
            "data/raw/psi/manifest.json is missing. Run:\n"
            "    python data/scripts/fetch_psi.py"
        )
    return json.loads(MANIFEST.read_text(encoding="utf-8"))["investigations"]


def build_from_psi(report: list[str]) -> list[dict]:
    manifest = load_manifest()
    records: list[dict] = []
    seen: set[str] = set()

    for source in SOURCES:
        entry = manifest.get(source.accession)
        path = RAW / source.accession / source.table
        if entry is None or not path.exists():
            report.append(f"{source.accession:<8} {source.prefix:<16} SKIPPED (file missing)")
            continue

        kept = dropped = 0
        reasons: dict[str, int] = {}
        for row in read_table(path):
            record, why = build_record(source, row, entry["acronym"] or source.accession, entry["page"])
            if record is None:
                dropped += 1
                reasons[why] = reasons.get(why, 0) + 1
                continue
            if not record["id"]:
                dropped += 1
                reasons["no test id"] = reasons.get("no test id", 0) + 1
                continue
            base_id, n = record["id"], 1
            while record["id"] in seen:
                n += 1
                record["id"] = f"{base_id}-{n}"
            seen.add(record["id"])
            records.append(record)
            kept += 1

        detail = ", ".join(f"{k} {v}" for k, v in sorted(reasons.items())) or "none"
        report.append(f"{source.accession:<8} {source.prefix:<16} kept {kept:>3}  dropped {dropped:>3}  ({detail})")

    return records


def build_from_curated(report: list[str]) -> list[dict]:
    """The hand-transcribed Saffire IV-VI rows, plus the edge-case fixtures if present."""
    if not CURATED.exists():
        report.append("curated  (missing)")
        return []
    rows = json.loads(CURATED.read_text(encoding="utf-8"))
    kept = [row for row in rows if not str(row.get("id", "")).startswith("fixture-")]
    report.append(f"curated  kept {len(kept):>3}  ({CURATED.relative_to(ROOT)})")
    return kept


def build() -> tuple[list[dict], list[str]]:
    report: list[str] = []
    records = build_from_psi(report)
    records += build_from_curated(report)
    records.sort(key=lambda record: record["id"])
    return records, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print the report, write nothing")
    parser.add_argument("--check", action="store_true", help="exit 1 if tests.json is out of date")
    args = parser.parse_args(argv)

    records, report = build()

    print(f"built {len(records)} records")
    for line in report:
        print("  " + line)

    if args.dry_run:
        return 0

    payload = json.dumps(records, indent=1, ensure_ascii=False) + "\n"
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != payload:
            print(f"\n{OUTPUT.relative_to(ROOT)} is out of date; run build_tests.py", file=sys.stderr)
            return 1
        print(f"\n{OUTPUT.relative_to(ROOT)} is up to date")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(payload, encoding="utf-8")
    print(f"\nwrote {OUTPUT.relative_to(ROOT)} ({date.today().isoformat()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
