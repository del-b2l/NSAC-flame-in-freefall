"""Ranking for Flame in Freefall.

Owner: Shaheer.

It sorts NASA fire tests so the ones whose air conditions are closest to the
chosen habitat come first. The rule is written in plain words in
`docs/ranking_rule.md`. If this file and that document disagree, the document
is right and this file is the bug.
"""

from backend.models import Habitat, TestRecord


def rank_tests(tests: list[TestRecord], habitat: Habitat) -> list[TestRecord]:
    """Return `tests` ordered from closest to `habitat` to furthest away.

    STATUS: skeleton, deliberately not implemented. The input list is returned
    unchanged so `POST /rank` keeps working while the rule is written.

    Intended rule (see `docs/ranking_rule.md`):

    1. oxygen_delta   = abs(test.oxygen_pct   - habitat.oxygen_pct)
    2. pressure_delta = abs(test.pressure_psi - habitat.pressure_psi)
    3. distance       = oxygen_delta + pressure_delta
    4. Sort by distance, smallest first.
    5. A test missing oxygen or pressure is kept, but placed after every test
       that has both. Missing values are never guessed or filled in.
    6. Ties break deterministically (airflow, then id) so the order never
       changes between two identical requests.
    """
    return tests
