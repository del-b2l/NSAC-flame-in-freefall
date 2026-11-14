"""Tests for the ranking rule.

Owner: Shaheer. The rule these tests check is written out in
`docs/ranking_rule.md`; if a test and the document disagree, one of them is a
bug and the PR that changes it has to change both.
"""

import pytest

from backend.data_loader import load_habitats, load_tests
from backend.models import Habitat
from backend.models import TestRecord as Record  # alias: pytest collects Test*
from backend.ranking import _distance, rank_tests

MOON_BASE = Habitat(name="Moon base", oxygen_pct=30, pressure_psi=10.2)


def make(
    test_id: str,
    oxygen_pct: float | None = None,
    pressure_psi: float | None = None,
    airflow: str | None = None,
) -> Record:
    """A throwaway record, for testing the rule rather than the data."""
    return Record(
        id=test_id,
        investigation="test",
        oxygen_pct=oxygen_pct,
        pressure_psi=pressure_psi,
        airflow=airflow,
    )


def ids(tests: list[Record]) -> list[str]:
    return [test.id for test in tests]


# --- the rule, as written in docs/ranking_rule.md ---------------------------


def test_worked_example_from_the_rule_document():
    """Moon base vs Saffire VI-3: 0.3 oxygen + 2.3 pressure = 2.6."""
    test = next(t for t in load_tests() if t.id == "saffire-vi-3")
    assert _distance(test, MOON_BASE) == pytest.approx(2.6)


def test_closest_test_comes_first():
    exact = make("exact", 30.0, 10.2)
    near = make("near", 30.5, 10.4)
    far = make("far", 60.0, 4.0)
    assert ids(rank_tests([far, near, exact], MOON_BASE)) == ["exact", "near", "far"]


def test_a_habitat_identical_to_a_test_gives_that_test_first():
    twin = make("twin", 30.0, 10.2)
    other = make("other", 30.0, 10.3)
    assert ids(rank_tests([other, twin], MOON_BASE)) == ["twin", "other"]


def test_oxygen_and_pressure_gaps_weigh_the_same():
    """1 mol % of oxygen costs the same as 1 psi of pressure."""
    oxygen_gap = make("a-oxygen", 31.0, 10.2)  # 1.0
    pressure_gap = make("b-pressure", 30.0, 11.2)  # 1.0
    assert ids(rank_tests([pressure_gap, oxygen_gap], MOON_BASE)) == [
        "a-oxygen",
        "b-pressure",
    ]


def test_distance_breaks_ties_before_the_id():
    closer = make("zzz", 30.3, 10.2)  # 0.3, sorts first despite the id
    further = make("aaa", 30.4, 10.2)  # 0.4
    assert ids(rank_tests([further, closer], MOON_BASE)) == ["zzz", "aaa"]


# --- airflow ---------------------------------------------------------------


def test_recorded_airflow_wins_inside_the_same_band():
    documented = make("documented", 30.3, 10.2, "20 cm/s concurrent")  # 0.3
    silent = make("silent", 30.2, 10.2, None)  # 0.2, same half-unit band
    assert ids(rank_tests([silent, documented], MOON_BASE)) == [
        "documented",
        "silent",
    ]


def test_airflow_does_not_beat_a_clearly_closer_test():
    close = make("close", 30.1, 10.2, None)  # 0.1
    ventilated = make("ventilated", 30.7, 10.2, "20 cm/s concurrent")  # 0.7
    assert ids(rank_tests([ventilated, close], MOON_BASE)) == ["close", "ventilated"]


def test_blank_airflow_counts_as_missing():
    blank = make("blank", 30.3, 10.2, "   ")
    recorded = make("recorded", 30.2, 10.2, "5 cm/s opposed")
    assert ids(rank_tests([blank, recorded], MOON_BASE)) == ["recorded", "blank"]


# --- missing values --------------------------------------------------------


def test_distance_is_none_when_pressure_is_missing():
    assert _distance(make("no-pressure", 30.0, None), MOON_BASE) is None


def test_distance_is_none_when_oxygen_is_missing():
    assert _distance(make("no-oxygen", None, 10.2), MOON_BASE) is None


def test_missing_pressure_goes_after_every_scored_test():
    scored = make("scored", 60.0, 4.0)  # far away, but scored
    missing = make("missing", 30.0, None)  # looks close, but incomplete
    assert ids(rank_tests([missing, scored], MOON_BASE)) == ["scored", "missing"]


def test_missing_oxygen_goes_after_every_scored_test():
    scored = make("scored", 60.0, 4.0)
    missing = make("missing", None, 10.2)
    assert ids(rank_tests([missing, scored], MOON_BASE)) == ["scored", "missing"]


def test_missing_values_are_kept_not_dropped():
    tests = [make("scored", 30.0, 10.2), make("empty"), make("half", 30.0, None)]
    assert sorted(ids(rank_tests(tests, MOON_BASE))) == ["empty", "half", "scored"]


# --- shape and stability ---------------------------------------------------


def test_empty_list_is_returned_empty():
    assert rank_tests([], MOON_BASE) == []


def test_single_record_is_returned_unchanged():
    only = make("only", 12.0, 3.0)
    assert ids(rank_tests([only], MOON_BASE)) == ["only"]


def test_same_request_always_gives_the_same_order():
    tests = load_tests()
    first = ids(rank_tests(tests, MOON_BASE))
    second = ids(rank_tests(tests, MOON_BASE))
    assert first == second


def test_input_list_is_not_reordered():
    tests = [make("c", 30.4, 10.2), make("b", 30.0, 10.2), make("a", 30.9, 10.2)]
    rank_tests(tests, MOON_BASE)
    assert ids(tests) == ["c", "b", "a"]


# --- against the real data -------------------------------------------------


def test_every_test_is_returned_for_every_habitat():
    tests = load_tests()
    assert tests, "no test data loaded"
    for habitat in load_habitats():
        assert len(rank_tests(tests, habitat)) == len(tests)


def test_real_data_keeps_unscored_tests_at_the_bottom():
    """A test missing oxygen or pressure is ranked last, never guessed."""
    tests = load_tests()
    for habitat in load_habitats():
        ranked = rank_tests(tests, habitat)
        scored = [t for t in ranked if t.oxygen_pct is not None and t.pressure_psi is not None]
        unscored = [t for t in ranked if t.oxygen_pct is None or t.pressure_psi is None]
        assert ranked[: len(scored)] == scored
        if unscored:
            assert ranked[-len(unscored) :] == unscored


def test_real_data_distances_never_go_backwards():
    tests = load_tests()
    for habitat in load_habitats():
        distances = [
            _distance(t, habitat)
            for t in rank_tests(tests, habitat)
            if t.oxygen_pct is not None and t.pressure_psi is not None
        ]
        assert distances == sorted(distances)


def test_real_saffire_order_for_the_moon_base():
    ranked = rank_tests(load_tests(), MOON_BASE)
    saffire = [t.id for t in ranked if t.id.startswith("saffire")]
    assert saffire == [
        "saffire-vi-3",
        "saffire-vi-2",
        "saffire-vi-4",
        "saffire-v-2",
        "saffire-iv-1",
    ]
