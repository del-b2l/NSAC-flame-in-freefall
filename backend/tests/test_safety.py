"""The safety table: nearest test per cell, the oxygen cut-off and the rule note."""

from fastapi.testclient import TestClient

from backend import safety
from backend.main import app
from backend.models import Habitat

client = TestClient(app)

HABITATS = [
    Habitat(name="Near", oxygen_pct=30.0, pressure_psi=10.0),
    Habitat(name="Edge", oxygen_pct=20.0, pressure_psi=10.0),
    Habitat(name="Far", oxygen_pct=19.9, pressure_psi=10.0),
]
TEST = {"test_id": "t-1", "oxygen_pct": 30.0, "pressure_psi": 9.0, "result": "Burn 10 s",
        "source_url": "https://ntrs.nasa.gov/citations/1"}
RULE = {"title": "Rule", "text": "Five samples.", "source_label": "Standard",
        "source_url": "https://standards.nasa.gov/x.pdf"}


def table(monkeypatch, materials, standard_rule=None):
    monkeypatch.setattr(safety, "load_habitats", lambda: HABITATS)
    monkeypatch.setattr(
        safety, "load_safety",
        lambda: {"materials": materials, "rules": None, "standard_rule": standard_rule},
    )
    return safety.safety_table()


def cells(result):
    return {cell["habitat"]: cell for cell in result["rows"][0]["cells"]}


def test_a_close_test_is_marked_tested_with_its_gaps(monkeypatch):
    cell = cells(table(monkeypatch, [{"material": "Cloth", "tests": [TEST]}]))["Near"]
    assert cell["state"] == "tested"
    assert cell["nearest_test"]["test_id"] == "t-1"
    assert (cell["oxygen_gap"], cell["pressure_gap"], cell["distance"]) == (0.0, 1.0, 1.0)


def test_a_test_exactly_at_the_cutoff_still_counts(monkeypatch):
    cell = cells(table(monkeypatch, [{"material": "Cloth", "tests": [TEST]}]))["Edge"]
    assert cell["oxygen_gap"] == safety.OXYGEN_CUTOFF_POINTS
    assert cell["state"] == "tested"


def test_a_test_beyond_the_cutoff_is_not_tested_but_keeps_its_reference(monkeypatch):
    cell = cells(table(monkeypatch, [{"material": "Cloth", "tests": [TEST]}]))["Far"]
    assert cell["oxygen_gap"] > safety.OXYGEN_CUTOFF_POINTS
    assert cell["state"] == "missing"
    assert cell["nearest_test"]["test_id"] == "t-1"
    assert cell["nearest_test"]["source_url"] == TEST["source_url"]


def test_a_material_with_no_usable_test_has_no_reference(monkeypatch):
    no_pressure = {**TEST, "pressure_psi": None}
    result = table(monkeypatch, [{"material": "Cloth", "tests": [no_pressure]}])
    for cell in result["rows"][0]["cells"]:
        assert cell["state"] == "missing"
        assert cell["nearest_test"] is None


def test_the_rule_is_returned_once_and_never_as_a_cell_state(monkeypatch):
    result = table(monkeypatch, [{"material": "Cloth", "tests": [TEST]}], standard_rule=RULE)
    assert result["standard_rule"] == RULE
    assert result["oxygen_cutoff_points"] == safety.OXYGEN_CUTOFF_POINTS
    assert all(cell["state"] != "rule" for cell in result["rows"][0]["cells"])


def test_real_table_spacesuit_column_is_not_tested_with_references():
    body = client.get("/safety/table").json()
    assert body["standard_rule"]["source_url"].startswith("https://standards.nasa.gov/")
    assert "15 cm" in body["standard_rule"]["text"]
    for row in body["rows"]:
        by_habitat = {cell["habitat"]: cell for cell in row["cells"]}
        suit = by_habitat["Spacesuit"]
        assert suit["state"] == "missing", row["material"]
        assert suit["nearest_test"] is not None, row["material"]
        assert suit["oxygen_gap"] > body["oxygen_cutoff_points"]
        for name in ("Earth", "Space station", "Moon base", "Rover"):
            assert by_habitat[name]["state"] == "tested", (row["material"], name)
