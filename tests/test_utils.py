from quiz_automation.utils import hash_text


def test_hash_text_deterministic():
    assert hash_text("quiz") == hash_text("quiz")


def test_hash_text_different():
    assert hash_text("a") != hash_text("b")
