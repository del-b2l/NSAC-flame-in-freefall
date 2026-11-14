#!/usr/bin/env python3
"""Write `docs/data_report.md`, a short summary of what the dataset holds.

Every number in the report is computed here from the processed files, the PSI
manifest and NASA's metadata, so the report cannot drift from the data. Run it
after `build_tests.py` and `build_investigations.py`.

Usage
-----
    python data/scripts/build_report.py            # write docs/data_report.md
    python data/scripts/build_report.py --check    # exit 1 if it is stale
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import build_tests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "psi"
MANIFEST = RAW / "manifest.json"
PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "docs" / "data_report.md"

NONE = "none in the table"

# Oxygen, pressure and airflow headers in the tables that do not produce
# records. Each header is checked against the CSV when the report is built.
OTHER_COLUMNS: dict[str, tuple[str | None, str | None, str | None]] = {
    "PSI-20": ("Oxygen Conc (percent)", None, None),
    "PSI-23": ("Atmosphere*", None, None),
    "PSI-25": ("Calibrated initial O2 % by vol", None, None),
    "PSI-68": ("Oxygen Mole Fraction", "Ambient Pressure (atm)", "Flow Velocity (cm/s)"),
    "PSI-98": ("Percent O2", None, "Air Flow (cm/s)"),
    "PSI-99": ("Percent O2 (Note 1)", None, "Air Flow (cm/s)"),
    "PSI-100": (None, None, "Air Flow"),
    "PSI-101": (None, None, "Inlet velocity (cm/s)"),
    "PSI-102": (None, None, "Air Flow (cm/s)"),
    "PSI-107": (None, None, "Air Rate (cm/s)"),
}

# Extra detail for investigations whose table cannot give one record per test.
NOTES: dict[str, str] = {
    "PSI-20": "NASA's notes say the chamber pressures were varied but are not identified in this summary table; "
    "oxygen is a list per day (e.g. `21; 26.5; 40`)",
    "PSI-23": "atmosphere is approximate text (e.g. `~21% O2 with N2`), one row per test day",
    "PSI-68": "the table lists the settings tested per fuel (e.g. `0.17; 0.21;0.25; 0.3`), not one row per test",
    "PSI-106": "the table lists test dates and fuel types only",
    "PSI-142": "the table lists derived data sets and their publications, not tests",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def headers(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    first = next(csv.reader(text.splitlines()))
    return {build_tests.normalise_key(h) for h in first}


def size(n: float) -> str:
    """Decimal units, as NASA's archive sizes are byte counts."""
    for unit, scale in (("TB", 1e12), ("GB", 1e9), ("MB", 1e6), ("kB", 1e3)):
        if n >= scale:
            return f"{n / scale:.2f} {unit}"
    return f"{int(n)} B"


def span(values: list[float], unit: str) -> str:
    if not values:
        return "-"
    return f"{min(values):g} to {max(values):g}{unit}"


def code(text: str | None) -> str:
    return f"`{text}`" if text else NONE


def cell(text: object) -> str:
    return str(text).replace("|", "/").replace("\n", " ")


def columns_for(accession: str, tables: list[Path]) -> tuple[list[str], list[str], list[str], bool]:
    """Oxygen, pressure and airflow headers for one investigation, and whether they feed records."""
    sources = [s for s in build_tests.SOURCES if s.accession == accession]
    if sources:
        oxygen = sorted({s.oxygen_col for s in sources})
        pressure = sorted({s.pressure_col for s in sources})
        return oxygen, pressure, [], True
    oxygen_col, pressure_col, airflow_col = OTHER_COLUMNS.get(accession, (None, None, None))
    found = set().union(*(headers(t) for t in tables)) if tables else set()
    for name in (oxygen_col, pressure_col, airflow_col):
        if name and name not in found:
            raise SystemExit(f"{accession}: column {name!r} is not in its table")
    as_list = [[c] if c else [] for c in (oxygen_col, pressure_col, airflow_col)]
    return as_list[0], as_list[1], as_list[2], False


def no_record_reason(tables: list[Path], oxygen: list[str], pressure: list[str], note: str | None) -> str:
    if not tables:
        reason = "NASA publishes no experimental table for it"
    elif oxygen and pressure:
        reason = "the table has oxygen and pressure columns but no single value per test"
    elif oxygen:
        reason = f"the table has oxygen (`{oxygen[0]}`) but no pressure"
    else:
        reason = "the table has no oxygen or pressure column"
    return f"{reason}; {note}" if note else reason


def render() -> str:
    full_manifest = load_json(MANIFEST)
    manifest = full_manifest["investigations"]
    skipped = full_manifest.get("skipped", [])
    investigations = load_json(PROCESSED / "investigations.json")
    records = load_json(PROCESSED / "tests.json")

    kept_ids = [item["id"] for item in investigations]
    meta = {a: load_json(RAW / a / "_investigation.json") for a in manifest}
    # Non-combustion hits are recorded by fetch_psi.py and never downloaded.
    # Anything else in the manifest that build_investigations.py left out is
    # listed too, so a dropped investigation is never silent.
    dropped = [(s["accession"], s["title"], s["researchArea"]) for s in skipped]
    dropped += [(a, meta[a]["title"], meta[a]["researchArea"]) for a in manifest if a not in kept_ids]

    kept_tables = [RAW / a / t["file"] for a in kept_ids for t in manifest[a]["tables"]]
    downloaded = sum(p.stat().st_size for p in kept_tables if p.exists())
    archive = {a: float(meta[a]["totalFileSize"] or 0) for a in kept_ids}

    by_inv: dict[str | None, list[dict]] = {}
    for record in records:
        by_inv.setdefault(record["investigation_id"], []).append(record)
    producing = [a for a in kept_ids if by_inv.get(a)]
    ntrs = by_inv.get(None, [])

    lines: list[str] = []
    add = lines.append
    add("# Data report")
    add("")
    add("This page says what data the app uses, where each number comes from, and what we left out.")
    add("All tables below are generated by `data/scripts/build_report.py` from the processed files and")
    add("NASA's own metadata, so they always match the data the app ships.")
    add("")
    add("## Totals")
    add("")
    add("| | Count |")
    add("|---|---|")
    add(f"| Investigations returned by the PSI combustion search | {len(manifest) + len(skipped)} |")
    add(f"| Skipped because NASA files them under another research area (not downloaded) | {len(skipped)} |")
    add(f"| Combustion investigations kept (NASA research area \"Combustion Science\") | {len(kept_ids)} |")
    add(f"| Experimental tables downloaded from PSI for kept investigations "
        f"| {sum(1 for p in kept_tables if p.exists())} of {len(kept_tables)} |")
    add(f"| Kept investigations that produce test records | {len(producing)} |")
    add(f"| Test records in `data/processed/tests.json` | {len(records)} |")
    add(f"| of which from PSI tables | {len(records) - len(ntrs)} |")
    add(f"| of which Saffire IV-VI, typed from the NTRS paper (not in PSI) | {len(ntrs)} |")
    add("")
    add("## How much data NASA holds")
    add("")
    add(f"NASA's metadata gives an archive size (`totalFileSize`) for each investigation. For the "
        f"{len(kept_ids)} kept investigations it adds up to **{size(sum(archive.values()))}** "
        f"({sum(archive.values()):,.0f} bytes). That is NASA's stated size of everything archived "
        "on PSI, not what we downloaded. We downloaded only the experimental "
        f"summary tables, {size(downloaded)} in total for the kept investigations, plus each "
        "investigation's metadata. The per-investigation figure is in the table below.")
    add("")
    add("## Every kept investigation")
    add("")
    add("Oxygen and pressure columns are the NASA headers. Only the four investigations with tests "
        "feed records; for the others the header is shown so you can see what is missing. "
        "Airflow is never filled for PSI records (it stays null).")
    add("")
    add("| PSI ID | Title | DOI | Tests | Oxygen column | Pressure column | Airflow column "
        "| Oxygen (%) | Pressure (psi) | NASA archive |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    reasons: list[tuple[str, str]] = []
    for item in investigations:
        accession = item["id"]
        tables = [RAW / accession / t["file"] for t in manifest[accession]["tables"]]
        oxygen, pressure, airflow, used = columns_for(accession, tables)
        rows = by_inv.get(accession, [])
        if not used:
            reasons.append((accession, no_record_reason(tables, oxygen, pressure, NOTES.get(accession))))
        doi = f"[{item['doi']}](https://doi.org/{item['doi']})" if item["doi"] else "-"
        add("| " + " | ".join([
            f"[{accession}]({item['landing_url']})",
            cell(item["name"]),
            doi,
            str(len(rows)),
            ", ".join(code(c) for c in oxygen) or NONE,
            ", ".join(code(c) for c in pressure) or NONE,
            ", ".join(code(c) for c in airflow) or NONE,
            span([r["oxygen_pct"] for r in rows], ""),
            span([r["pressure_psi"] for r in rows], ""),
            size(archive[accession]),
        ]) + " |")
    add("")
    add("Units and conversion for the tables that feed records (oxygen is stored as mol %, pressure as psi):")
    add("")
    add("| PSI ID | Table | Oxygen | Pressure | Records |")
    add("|---|---|---|---|---|")
    for source in build_tests.SOURCES:
        count = sum(1 for r in records if r.get("conditions", {}).get("Table") == source.table)
        factor = build_tests.PSI_PER[source.pressure_unit.lower()]
        add(f"| {source.accession} | {source.table} | `{source.oxygen_col}`, mole fraction x {source.oxygen_scale:g} "
            f"| `{source.pressure_col}`, {source.pressure_unit} x {factor:g} | {count} |")
    add("")
    add("In the two inverse-flame tables the oxygen flows out of the burner into a chamber that holds the fuel, "
        "so `XO2` there describes the burner gas, not the chamber air.")
    for source in build_tests.SOURCES:
        if source.result_col:
            values = sorted({
                str(r["conditions"].get(source.result_col)) for r in records
                if r.get("conditions", {}).get("Table") == source.table and r["conditions"].get(source.result_col)
            })
            add("")
            add(f"`result` is filled only where a column states the outcome: {source.accession} `{source.result_col}` "
                f"({', '.join(values)}). Other PSI records have a null `result`; "
                "the Saffire IV-VI records carry the outcome typed from the NTRS paper.")
    add("")
    add("## Kept investigations with no test records")
    add("")
    add("A record needs a numeric oxygen value and a numeric pressure for the same test. These do not have that:")
    add("")
    for accession, reason in reasons:
        add(f"- **{accession}**: {reason}.")
    add("")
    add("## Investigations dropped")
    add("")
    add("The PSI search is a text match on \"combustion\", so it also returns investigations from other "
        "research areas. `fetch_psi.py` lists these under `skipped` in the manifest and does not download them:")
    add("")
    for accession, title, area in dropped:
        add(f"- **{accession}** ({title}): NASA files it under \"{area}\", not \"Combustion Science\".")
    add("")
    add("## Rules we followed")
    add("")
    add("Nothing is guessed. A value is filled only when a NASA table states it; anything missing is null, "
        "and rows without both oxygen and pressure are left out rather than filled in. Raw files are never "
        "edited: the build scripts in `data/scripts/` read them, convert units, and write the processed "
        "files, and the tests in `data/tests/` check the output against the raw rows. Every PSI record "
        "keeps every original column under its NASA header and links to its PSI investigation page; the five "
        "Saffire IV-VI records link to the NTRS paper they were typed from.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if docs/data_report.md is out of date")
    args = parser.parse_args(argv)

    payload = render()
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != payload:
            print(f"{OUTPUT.relative_to(ROOT)} is out of date; run build_report.py", file=sys.stderr)
            return 1
        print(f"{OUTPUT.relative_to(ROOT)} is up to date")
        return 0

    OUTPUT.write_text(payload, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
