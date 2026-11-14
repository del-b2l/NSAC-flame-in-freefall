"""Ranking for Flame in Freefall.

Owner: Shaheer.

It sorts NASA fire tests so the ones whose air conditions are closest to the
chosen habitat come first. The rule is written in plain words in
`docs/ranking_rule.md`. If this file and that document disagree, the document
is right and this file is the bug.
"""

import math

from backend.models import Habitat, TestRecord

# Two tests whose distances differ by less than half a unit are treated as
# equally close; airflow then decides which one comes first. NASA publishes no
# airflow figure for the habitats, so airflow is a tie-break and never a
# distance term. See docs/ranking_rule.md, "Airflow".
BAND_WIDTH = 0.5


def _distance(test: TestRecord, habitat: Habitat) -> float | None:
    """Oxygen gap plus pressure gap, in their own units (mol % and psi).

    Returns None when the test is missing oxygen or pressure. Missing values
    are never guessed or filled in from another test.
    """
    if test.oxygen_pct is None or test.pressure_psi is None:
        return None
    return abs(test.oxygen_pct - habitat.oxygen_pct) + abs(
        test.pressure_psi - habitat.pressure_psi
    )


def _has_airflow(test: TestRecord) -> bool:
    """True when the source recorded an airflow for this test."""
    return bool(test.airflow and test.airflow.strip())


def _sort_key(test: TestRecord, habitat: Habitat) -> tuple[int, int, int, float, str]:
    """Sort key: scored tests first, then closeness, then airflow, then id."""
    distance = _distance(test, habitat)
    airflow = 0 if _has_airflow(test) else 1

    if distance is None:
        # Kept, but after every test that has both oxygen and pressure.
        return (1, 0, airflow, 0.0, test.id)

    band = math.floor(distance / BAND_WIDTH + 1e-9)
    return (0, band, airflow, distance, test.id)


def rank_tests(tests: list[TestRecord], habitat: Habitat) -> list[TestRecord]:
    """Return `tests` ordered from closest to `habitat` to furthest away.

    The order is:

    1. Tests that have both oxygen and pressure, closest first, where
       ``distance = |oxygen_pct - habitat.oxygen_pct| + |pressure_psi - habitat.pressure_psi|``.
    2. Tests inside the same half-unit band count as equally close, and the one
       with a recorded airflow goes first.
    3. Tests missing oxygen or pressure, after all of the above.
    4. Within every group, ``id`` breaks the remaining ties, so the same
       request always returns the same order.

    The input list is not modified.
    """
    return sorted(tests, key=lambda test: _sort_key(test, habitat))

# Batool's edit to match the decided tiering system.

def rank_tests_by_tier(tests: list[TestRecord], habitat: Habitat) -> list[dict]:
    """Rank tests by measurement completeness, then distance."""

    results = []

    for test in tests:
        has_oxygen = test.oxygen_pct is not None
        has_pressure = test.pressure_psi is not None

        if has_oxygen and has_pressure:
            tier = 1
            scored_on = ["oxygen_pct", "pressure_psi"]
            label = "scored on oxygen and pressure"

        elif has_oxygen:
            tier = 2
            scored_on = ["oxygen_pct"]
            label = "scored on oxygen only"

        elif has_pressure:
            tier = 2
            scored_on = ["pressure_psi"]
            label = "scored on pressure only"

        else:
            tier = 3
            scored_on = []
            label = "not scored"

        distance = None

        if has_oxygen:
            distance = abs(test.oxygen_pct - habitat.oxygen_pct)

        if has_pressure:
            pressure_difference = abs(
                test.pressure_psi - habitat.pressure_psi
            )
            distance = (
                pressure_difference
                if distance is None
                else distance + pressure_difference
            )

        results.append({
            "test": test,
            "tier": tier,
            "scored_on": scored_on,
            "distance": distance,
            "label": label,
        })

    return sorted(
        results,
        key=lambda result: (
            result["tier"],
            result["distance"] if result["distance"] is not None else 0,
            result["test"].id,
        ),
    )