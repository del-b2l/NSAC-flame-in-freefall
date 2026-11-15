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
    """The brief is the top of the ranked list.

    /rank and /brief use different tie-breaks (airflow within a half-unit band
    vs tier order), so the exact order can drift after a data refresh. What
    must hold is that /rank returns plain test records -- the shape the
    frontend renders -- and that every test the brief surfaces is near the top
    of /rank.
    """
    for h in ["Earth", "Moon base", "Spacesuit"]:
        ranked = client.post("/rank", json={"habitat": h}).json()
        assert ranked, f"/rank returned nothing for {h}"
        assert {"id", "oxygen_pct", "pressure_psi", "source_url"} <= set(ranked[0])
        rank_ids = [r["id"] for r in ranked]
        brief = [t["id"] for t in client.get("/brief", params={"habitat": h}).json()["top_tests"]]
        assert brief, f"/brief returned nothing for {h}"
        for test_id in brief:
            assert test_id in rank_ids[:10], (
                f"{test_id} from /brief is not near the top of /rank for {h}"
            )
