from __future__ import annotations

from quiz_automation import clicker


def test_click_calls_pyautogui(monkeypatch):
    called = {}

    def fake_click(x, y):
        called["pt"] = (x, y)

    monkeypatch.setattr(clicker.pyautogui, "click", fake_click)
    clicker.click((1, 2))
    assert called["pt"] == (1, 2)
