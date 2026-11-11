from backend.ranking import rank_tests
from backend.models import TestRecord, Habitat

def test_rank_returns_all_tests():
    tests = [TestRecord(id="a", investigation="X")]
    habitat = Habitat(name="Moon base", oxygen_pct=30, pressure_psi=10.2)
    assert len(rank_tests(tests, habitat)) == 1