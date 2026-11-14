import pytest

from backend.models import Habitat, TestRecord as NASARecord
from backend.ranking import rank_tests_by_tier


def make_test(test_id, oxygen=None, pressure=None):
    return NASARecord(
        id=test_id,
        investigation=f"Investigation {test_id}",
        oxygen_pct=oxygen,
        pressure_psi=pressure,
    )


def test_tier_assignment():
    habitat = Habitat(name="Moon base", oxygen_pct=30, pressure_psi=10.2)

    tests = [
        make_test("both", 31, 11),
        make_test("oxygen-only", 32, None),
        make_test("pressure-only", None, 12),
        make_test("neither", None, None),
    ]

    results = rank_tests_by_tier(tests, habitat)
    by_id = {result["test"].id: result for result in results}

    assert by_id["both"]["tier"] == 1
    assert by_id["oxygen-only"]["tier"] == 2
    assert by_id["pressure-only"]["tier"] == 2
    assert by_id["neither"]["tier"] == 3


def test_tier_distances_and_labels():
    habitat = Habitat(name="Moon base", oxygen_pct=30, pressure_psi=10.2)

    tests = [
        make_test("both", 31, 12),
        make_test("oxygen-only", 32, None),
        make_test("pressure-only", None, 12),
        make_test("neither", None, None),
    ]

    results = rank_tests_by_tier(tests, habitat)
    by_id = {result["test"].id: result for result in results}

    assert by_id["both"]["distance"] == pytest.approx(2.8)
    assert by_id["oxygen-only"]["distance"] == pytest.approx(2)
    assert by_id["pressure-only"]["distance"] == pytest.approx(1.8)
    assert by_id["neither"]["distance"] is None

    assert by_id["both"]["label"] == "scored on oxygen and pressure"
    assert by_id["oxygen-only"]["label"] == "scored on oxygen only"
    assert by_id["pressure-only"]["label"] == "scored on pressure only"
    assert by_id["neither"]["label"] == "not scored"


def test_tier_order_takes_priority_over_distance():
    habitat = Habitat(name="Moon base", oxygen_pct=30, pressure_psi=10.2)

    tests = [
        make_test("one-field", 30.1, None),
        make_test("two-fields", 50, 30),
        make_test("unscored", None, None),
    ]

    results = rank_tests_by_tier(tests, habitat)

    assert [r["test"].id for r in results] == [
        "two-fields",
        "one-field",
        "unscored",
    ]


def test_ties_are_broken_by_id():
    habitat = Habitat(name="Moon base", oxygen_pct=30, pressure_psi=10.2)

    tests = [
        make_test("test-b", 31, None),
        make_test("test-a", 31, None),
    ]

    results = rank_tests_by_tier(tests, habitat)

    assert [r["test"].id for r in results] == ["test-a", "test-b"]