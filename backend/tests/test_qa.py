from backend.qa import _verify

CTX = {"saffire-vi-3": {"record": {"oxygen_pct": 30.3, "result": "Burn 780 s; 1280 kJ"}}}


def test_valid_answer_passes():
    assert _verify("It burned for 780 s [saffire-vi-3].", CTX, "how long")[0]


def test_unknown_id_fails():
    assert not _verify("It burned [made-up-1].", CTX, "x")[0]


def test_number_not_in_record_fails():
    assert not _verify("It burned for 900 s [saffire-vi-3].", CTX, "x")[0]


def test_no_citation_fails():
    assert not _verify("It burned for 780 s.", CTX, "x")[0]