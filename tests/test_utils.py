from __future__ import annotations

from quiz_automation.utils import question_hash


def test_question_hash_stable():
    h1 = question_hash("What?")
    h2 = question_hash("What?")
    assert h1 == h2
