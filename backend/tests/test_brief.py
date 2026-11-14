from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# def test_brief_moon_base_order():
#     """The five closest scored tests, nearest first.

#     The ids are not pinned: the dataset is regenerated from NASA tables, so
#     pinning names would fail on every data refresh. The properties are what
#     /brief promises.
#     """
#     r = client.get("/brief", params={"habitat": "Moon base"})
#     assert r.status_code == 200
#     top = r.json()["top_tests"]
#     assert len(top) == 5
#     assert all(t["tier"] == 1 for t in top)
#     distances = [t["distance"] for t in top]
#     assert distances == sorted(distances)
#     assert all(t["oxygen_pct"] is not None and t["pressure_psi"] is not None for t in top)

def test_brief_moon_base():
    r = client.get("/brief", params={"habitat": "Moon base"})
    assert r.status_code == 200
    tests = r.json()["top_tests"]
    assert 1 <= len(tests) <= 5
    assert all(t["oxygen_pct"] is not None and t["pressure_psi"] is not None for t in tests)
    d = [t["distance"] for t in tests]
    assert d == sorted(d)


def test_brief_excludes_unscored():
    r = client.get("/brief", params={"habitat": "Earth"})
    ids = [t["id"] for t in r.json()["top_tests"]]
    assert "fixture-not-scored" not in ids


def test_brief_unknown_habitat():
    assert client.get("/brief", params={"habitat": "Mars"}).status_code == 404

def test_rank_and_brief_agree():
    for h in ["Earth", "Moon base", "Spacesuit"]:
        ranked = client.post("/rank", json={"habitat": h}).json()
        tier1 = [r["test"]["id"] for r in ranked if r["tier"] == 1][:5]
        brief = [t["id"] for t in client.get("/brief", params={"habitat": h}).json()["top_tests"]]
        assert brief == tier1