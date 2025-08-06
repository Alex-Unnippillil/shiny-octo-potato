from __future__ import annotations

from types import SimpleNamespace

from quiz_automation import gui as gui_module
from quiz_automation.gui import QuizGUI


class DummyTk:
    def __init__(self):
        self.title_called = None

    def title(self, text):
        self.title_called = text

    def mainloop(self):  # pragma: no cover - not needed
        pass

    def __getattr__(self, name):  # pragma: no cover - stub
        return lambda *a, **k: None


def test_gui_start_stop(monkeypatch):
    monkeypatch.setattr(gui_module.tk, "Tk", DummyTk)
    def fake_stringvar(value: str = "") -> SimpleNamespace:
        ns = SimpleNamespace(value=value)
        ns.get = lambda: ns.value
        ns.set = lambda v: setattr(ns, "value", v)
        return ns

    monkeypatch.setattr(gui_module.tk, "StringVar", fake_stringvar)
    monkeypatch.setattr(
        gui_module.tk, "Label", lambda *a, **k: SimpleNamespace(pack=lambda: None)
    )
    monkeypatch.setattr(
        gui_module.tk, "Button", lambda *a, **k: SimpleNamespace(pack=lambda: None)
    )
    g = QuizGUI()
    assert g.status_var.get() == "Idle"
    g.start()
    assert g.status_var.get() == "Running"
    g.stop()
    assert g.status_var.get() == "Stopped"
