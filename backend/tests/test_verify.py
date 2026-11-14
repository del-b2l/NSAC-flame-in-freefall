from backend.verify import check_grounded

SRC = {"a": "Burn 780 s; total 1280 kJ; smoke readily detected at 981 seconds"}


def test_supported_sentence_passes():
    assert check_grounded("The burn was 780 s [a].", SRC)[0]


def test_unsupported_claim_fails():
    assert not check_grounded("The flame was extinguished by water mist [a].", SRC)[0]


def test_uncited_sentence_fails():
    assert not check_grounded("The burn was 780 s.", SRC)[0]


def test_implicit_source_passes():
    assert check_grounded("The burn was 780 s.", SRC, implicit_source="a")[0]


def test_wrong_number_fails():
    assert not check_grounded("The burn was 900 s [a].", SRC)[0]