"""Tests for the unit conversion and the built dataset.

The conversion tests use inline values, so they run offline. The tests that
rebuild from the raw PSI files skip themselves when `data/raw/psi/` is absent
(that folder is gitignored; run `fetch_psi.py` to restore it).
"""

import json
from pathlib import Path

import build_tests
import pytest
from build_tests import Source, build_record, parse_number, parse_pressure, to_psi

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed" / "tests.json"
RAW = ROOT / "data" / "raw" / "psi"


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return json.loads(PROCESSED.read_text(encoding="utf-8"))


# --- units -----------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [
        (14.7, "psi", 14.7),
        (1.0, "atm", 14.6959488),
        (1.0, "bar", 14.5037738),
        (101.325, "kPa", 14.6959488),
        (760.0, "mmHg", 14.6959488),
        (760.0, "torr", 14.6959488),
        (0.0, "bar", 0.0),
    ],
)
def test_to_psi_known_units(value, unit, expected):
    assert to_psi(value, unit) == pytest.approx(expected, rel=1e-6)


def test_to_psi_rejects_unknown_unit():
    with pytest.raises(ValueError):
        to_psi(1.0, "furlongs")


@pytest.mark.parametrize(
    ("text", "default_unit", "expected"),
    [
        ("1 atm", "bar", 14.6959488),
        ("0.9443956", "bar", 13.6973002),
        ("757.7", "mmHg", 14.6516193),
        ("13.8 psi", "bar", 13.8),
        ("1.5 BAR", "atm", 21.7556607),
    ],
)
def test_parse_pressure_reads_unit_or_defaults(text, default_unit, expected):
    assert parse_pressure(text, default_unit) == pytest.approx(expected, rel=1e-5)


@pytest.mark.parametrize("text", ["", "   ", None, "RAMPED", "n/a"])
def test_parse_pressure_returns_none_for_junk(text):
    assert parse_pressure(text, "atm") is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [("0.2071", 0.2071), (" 30.3 ", 30.3), ("22%", 22.0), ("1,024", 1024.0), ("", None), ("RAMPED", None)],
)
def test_parse_number(text, expected):
    assert parse_number(text) == expected


# --- row to record ---------------------------------------------------------

SOURCE = Source(
    accession="PSI-999",
    table="table.csv",
    prefix="demo",
    id_col="Test",
    oxygen_col="XO2",
    oxygen_scale=100.0,
    pressure_col="p",
    pressure_unit="bar",
    material_col="Fuel",
)
PAGE = "https://psi.nasa.gov/physci/repo/data/investigations/PSI-999"


def test_row_becomes_record():
    row = {"Test": "21088A1", "XO2": "0.3939", "p": "0.9443956", "Fuel": "ethane"}
    record, why = build_record(SOURCE, row, "CFI-G", PAGE)
    assert why == ""
    assert record["id"] == "demo-21088a1"
    assert record["investigation"] == "CFI-G"
    assert record["material"] == "ethane"
    assert record["oxygen_pct"] == 39.39
    assert record["pressure_psi"] == pytest.approx(13.7, abs=0.01)
    assert record["source_url"] == PAGE
    assert record["conditions"]["Accession"] == "PSI-999"
    assert record["conditions"]["XO2"] == "0.3939"  # raw value kept unchanged
    assert record["airflow"] is None  # not in this table, so not invented


def test_row_without_pressure_is_dropped():
    record, why = build_record(SOURCE, {"Test": "x", "XO2": "0.21", "p": ""}, "CFI-G", PAGE)
    assert record is None
    assert why == "no pressure"


def test_row_without_oxygen_is_dropped():
    record, why = build_record(SOURCE, {"Test": "x", "XO2": "RAMPED", "p": "1.0"}, "CFI-G", PAGE)
    assert record is None
    assert why == "no oxygen"


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        ({"Test": "x", "XO2": "1.5", "p": "1.0"}, "oxygen out of range (150.0)"),
        ({"Test": "x", "XO2": "0.21", "p": "0"}, "pressure out of range (0.0)"),
        ({"Test": "x", "XO2": "0.21", "p": "20"}, "pressure out of range (290.08)"),
    ],
)
def test_impossible_values_are_dropped(row, reason):
    record, why = build_record(SOURCE, row, "CFI-G", PAGE)
    assert record is None
    assert why == reason


def test_every_source_declares_a_known_unit():
    for source in build_tests.SOURCES:
        assert source.pressure_unit.lower() in build_tests.PSI_PER, source.prefix
        assert source.oxygen_scale > 0


def test_slug_is_lowercase_and_url_safe():
    assert build_tests.slug(" 21088 B1 ") == "21088-b1"
    assert build_tests.slug("PSI-159: CFI-G") == "psi-159-cfi-g"


# --- the built dataset -----------------------------------------------------


def test_dataset_is_not_empty(records):
    assert len(records) > 500


def test_ids_are_unique(records):
    ids = [record["id"] for record in records]
    assert len(ids) == len(set(ids))


def test_every_record_is_traceable(records):
    for record in records:
        assert record["source_url"], record["id"]
        assert record["source_url"].startswith("https://"), record["id"]
        assert record["investigation"], record["id"]


def test_fixture_rows_are_gone(records):
    assert not [record for record in records if record["id"].startswith("fixture-")]


def test_every_record_has_oxygen_and_pressure(records):
    for record in records:
        assert record["oxygen_pct"] is not None, record["id"]
        assert record["pressure_psi"] is not None, record["id"]
        assert 1.0 <= record["oxygen_pct"] <= 100.0, record["id"]
        assert 0.5 <= record["pressure_psi"] <= 100.0, record["id"]


def test_records_are_sorted_by_id(records):
    assert [record["id"] for record in records] == sorted(record["id"] for record in records)


@pytest.mark.parametrize(
    ("record_id", "oxygen_pct", "pressure_psi"),
    [
        ("cfig-normal-21088a1", 39.39, 13.70),  # CFI-G, 0.3939 and 0.9443956 bar
        ("flex-20cal08", 21.0, 14.65),  # FLEX, 0.21 and 757.7 mmHg
        ("cfi-1206", 21.0, 14.70),  # CFI, 0.21 and "1 atm"
        ("acme-fd-normal-19115a1", 20.71, 14.96),  # ACME/Flame Design, 1.01796816 atm
        ("saffire-vi-3", 30.3, 7.9),  # NTRS paper, transcribed by hand
    ],
)
def test_known_rows_survive_conversion(records, record_id, oxygen_pct, pressure_psi):
    record = next(item for item in records if item["id"] == record_id)
    assert record["oxygen_pct"] == pytest.approx(oxygen_pct, abs=0.01)
    assert record["pressure_psi"] == pytest.approx(pressure_psi, abs=0.01)


@pytest.mark.skipif(not RAW.exists(), reason="raw PSI files are not fetched in this checkout")
def test_processed_file_matches_a_fresh_build():
    fresh, _ = build_tests.build()
    on_disk = json.loads(PROCESSED.read_text(encoding="utf-8"))
    assert fresh == on_disk, "data/processed/tests.json is stale; run data/scripts/build_tests.py"
