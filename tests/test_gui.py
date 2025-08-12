from types import SimpleNamespace

from quiz_automation.gui import QuizGUI


def test_gui_start_stop(monkeypatch):
    started = {}

    class DummyWatcher:
        def __init__(self, *args, **kwargs):
            if len(args) >= 3:
                started['value'] = args[2]
            else:
                started['value'] = kwargs.get('poll_interval')
        def start(self):
            pass
        stop_flag = SimpleNamespace(set=lambda: None)

    class DummyWidget:
        def __init__(self, *args, **kwargs):
            pass

        def pack(self):
            pass

    class DummyTk(DummyWidget):
        def title(self, text):
            pass

        def after(self, ms, func):
            pass

        def mainloop(self):
            pass

    class DummyStringVar:
        def __init__(self, value=""):
            self.value = value

        def set(self, value: str) -> None:
            self.value = value

        def get(self) -> str:
            return self.value

    dummy_tk = SimpleNamespace(
        Tk=DummyTk, Button=DummyWidget, Label=DummyWidget, StringVar=DummyStringVar
    )
    monkeypatch.setenv("POLL_INTERVAL", "0.7")
    from quiz_automation.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setattr("quiz_automation.gui.tk", dummy_tk)
    monkeypatch.setattr("quiz_automation.gui.Watcher", DummyWatcher)
    gui = QuizGUI()
    gui.start()
    assert started['value'] == 0.7
    gui.stop()
    assert gui.watcher is None
