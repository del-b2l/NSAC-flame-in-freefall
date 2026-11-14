from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_brief_moon_base_order():
    r = client.get("/brief", params={"habitat": "Moon base"})
    assert r.status_code == 200
    ids = [t["id"] for t in r.json()["top_tests"]]
    assert ids == ["saffire-vi-3", "saffire-vi-2", "saffire-vi-4",
                   "saffire-v-2", "saffire-iv-1"]


def test_brief_excludes_unscored():
    r = client.get("/brief", params={"habitat": "Earth"})
    ids = [t["id"] for t in r.json()["top_tests"]]
    assert "fixture-not-scored" not in ids


def test_brief_unknown_habitat():
    assert client.get("/brief", params={"habitat": "Mars"}).status_code == 404