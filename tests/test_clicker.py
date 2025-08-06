from __future__ import annotations

from quiz_automation.clicker import compute_click


def test_compute_click_letter():
    assert compute_click((100, 200), "B") == (100, 240)
