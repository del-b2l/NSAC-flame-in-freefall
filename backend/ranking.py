from backend.models import TestRecord, Habitat

def rank_tests(tests: list[TestRecord], habitat: Habitat) -> list[TestRecord]:
    # TODO: score by closeness of oxygen, pressure, and airflow to the habitat
    return tests