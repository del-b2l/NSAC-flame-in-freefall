"""Check shipped records against the raw NASA rows they came from.

For every PSI table we use, two rows are pinned: the lowest and the highest
pressure in that table. The test reads the row straight from the CSV, does the
unit conversion here (not with the build script's helpers), and compares it
with the record in `data/processed/tests.json`.

The CSVs are not committed, so each case skips itself when its file is absent.
`data/raw/psi/` itself always exists because `manifest.json` is committed.
"""

import csv
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "psi"
PROCESSED = ROOT / "data" / "processed" / "tests.json"

# psi per unit (NIST SP 811). 1 mmHg = 1 atm / 760.
ATM = 14.6959488
BAR = 14.5037738
MMHG = ATM / 760.0

# (accession, table, id column, test id, oxygen column, pressure column, psi per unit)
PINNED = [
    ("PSI-159", "PSI-159_Experimental table_CFI-G_Normal Flames.csv", "Test", "21106 B1",
     "XO2 before test", "approx p (bar)", BAR),
    ("PSI-159", "PSI-159_Experimental table_CFI-G_Normal Flames.csv", "Test", "21130 G1",
     "XO2 before test", "approx p (bar)", BAR),
    ("PSI-159", "PSI-159_Experimental table_CFI-G_Inverse Flames.csv", "Test", "21196 K1",
     "XO2", "approx p (bar)", BAR),
    ("PSI-159", "PSI-159_Experimental table_CFI-G_Inverse Flames.csv", "Test", "21216 A1",
     "XO2", "approx p (bar)", BAR),
    ("PSI-10", "PSI-10_Experimental table_Flame Design_Normal Flame.csv", "Test", "19142G5",
     "XO2 (init)", "pmean (atm)", ATM),
    ("PSI-10", "PSI-10_Experimental table_Flame Design_Normal Flame.csv", "Test", "19189P1",
     "XO2 (init)", "pmean (atm)", ATM),
    ("PSI-10", "PSI-10_Experimental table_Flame Design_Inverse Flame.csv", "Test", "21349A1",
     "XO2", "pmean (atm)", ATM),
    ("PSI-10", "PSI-10_Experimental table_Flame Design_Inverse Flame.csv", "Test", "22027D2",
     "XO2", "pmean (atm)", ATM),
    ("PSI-69", "PSI-69_Experimental table_FLEX.csv", "FLEX Identifier", "C12M101",
     "O initial ambient composition; mole fraction", "Ambient pressure; mmHg", MMHG),
    ("PSI-69", "PSI-69_Experimental table_FLEX.csv", "FLEX Identifier", "256F002",
     "O initial ambient composition; mole fraction", "Ambient pressure; mmHg", MMHG),
    ("PSI-39", "PSI-39_Experimental table_CFI.csv", "Flex Number", "1356",
     "Oxygen", "Pressure", ATM),
    ("PSI-39", "PSI-39_Experimental table_CFI.csv", "Flex Number", "1340",
     "Oxygen", "Pressure", ATM),
]


def raw_row(path: Path, id_col: str, test_id: str) -> dict[str, str]:
    """Return the one CSV row whose id column equals `test_id`."""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    matches = []
    for row in csv.DictReader(text.splitlines()):
        clean = {" ".join(str(k).split()): (v or "").strip() for k, v in row.items() if k}
        if clean.get(id_col) == test_id:
            matches.append(clean)
    assert len(matches) == 1, f"{test_id} appears {len(matches)} times in {path.name}"
    return matches[0]


def number_only(text: str) -> float:
    """CFI writes pressure as `5 atm`; the other tables write a bare number."""
    return float(text.split()[0])


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return json.loads(PROCESSED.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("accession", "table", "id_col", "test_id", "oxygen_col", "pressure_col", "psi_per_unit"),
    PINNED,
    ids=[f"{row[0]}-{row[3]}" for row in PINNED],
)
def test_record_equals_converted_raw_row(
    records, accession, table, id_col, test_id, oxygen_col, pressure_col, psi_per_unit
):
    path = RAW / accession / table
    if not path.exists():
        pytest.skip(f"{path.name} is not fetched in this checkout")

    row = raw_row(path, id_col, test_id)
    matches = [
        r for r in records
        if r.get("conditions", {}).get("Table") == table and r["conditions"].get(id_col) == test_id
    ]
    assert len(matches) == 1, f"{test_id}: {len(matches)} records"
    record = matches[0]

    assert record["investigation_id"] == accession
    assert record["oxygen_pct"] == round(float(row[oxygen_col]) * 100, 2)
    assert record["pressure_psi"] == round(number_only(row[pressure_col]) * psi_per_unit, 2)


def test_highest_cfi_pressure_is_five_atm(records):
    """73.48 psi is the largest pressure in the dataset; it must be CFI's 5 atm."""
    top = max(records, key=lambda r: r["pressure_psi"])
    assert top["pressure_psi"] == 73.48
    assert top["conditions"]["Pressure"] == "5 atm"
