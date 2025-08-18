from types import SimpleNamespace

from quiz_automation.gui import QuizGUI
from quiz_automation.region_selector import Region
from quiz_automation.chatgpt_client import ChatGPTResponse


def _ensure_api_key(monkeypatch) -> None:
    """Ensure ChatGPTClient has an API key for instantiation."""
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_api_key", "test-key"
    )


def test_gui_start_stop(monkeypatch):
    _ensure_api_key(monkeypatch)
    started = {}

    class DummyWatcher:
        def __init__(self, *args, **kwargs):
            started['value'] = started.get('value', 0) + 1

        def start(self):
            pass

        def join(self):
            pass

        stop_flag = SimpleNamespace(set=lambda: None)

    class DummyWidget:
        def __init__(self, *args, command=None, **kwargs):
            self.command = command

        def pack(self, *args, **kwargs):
            pass

        def invoke(self):
            if self.command:
                self.command()

    class DummyTk(DummyWidget):
        def title(self, text):
            pass

        def after(self, ms, func):
            pass

        def protocol(self, name, func):
            pass

        def mainloop(self):
            pass

        def destroy(self):
            pass

    class DummyToplevel(DummyTk):
        def overrideredirect(self, flag):
            pass

        def attributes(self, *args, **kwargs):
            pass

        def geometry(self, spec):
            pass

        def lift(self):
            pass

    class DummyCanvas(DummyWidget):
        def create_rectangle(self, *args, **kwargs):
            pass

    class DummyStringVar:
        def __init__(self, value=""):
            self.value = value

        def set(self, value: str) -> None:
            self.value = value

        def get(self) -> str:
            return self.value

    dummy_tk = SimpleNamespace(
        Tk=DummyTk,
        Button=DummyWidget,
        Label=DummyWidget,
        StringVar=DummyStringVar,
        Canvas=DummyCanvas,
        Toplevel=DummyToplevel,
        BOTH="both",
    )
    calls = {'count': 0}

    def dummy_select_region() -> Region:
        calls['count'] += 1
        return Region(0, 0, 1, 1)

    class DummyLogger:
        def __init__(self, path):
            pass

        def log(self, *args, **kwargs):
            pass

        def close(self):
            pass

    monkeypatch.setattr("quiz_automation.gui.tk", dummy_tk)
    monkeypatch.setattr("quiz_automation.gui.Watcher", DummyWatcher)
    monkeypatch.setattr("quiz_automation.gui.select_region", dummy_select_region)
    monkeypatch.setattr("quiz_automation.gui.QuizLogger", DummyLogger)
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.OpenAI", lambda api_key: SimpleNamespace()
    )
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_api_key", "test-key"
    )
    monkeypatch.setattr(
        "quiz_automation.gui.ChatGPTClient.ask",
        lambda self, q: ChatGPTResponse("A", None, 0.0),
    )


    gui = QuizGUI()
    gui.start()
    gui.stop()
    gui.start()
    assert calls['count'] == 1
    assert started['value'] == 2
    gui.stop()
    assert gui.watcher is None


def test_select_region_button(monkeypatch):
    _ensure_api_key(monkeypatch)
    calls = {"count": 0}

    class DummyWatcher:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            pass

        def join(self):
            pass

        stop_flag = SimpleNamespace(set=lambda: None)

    class DummyWidget:
        def __init__(self, *args, command=None, **kwargs):
            self.command = command

        def pack(self, *args, **kwargs):
            pass

        def invoke(self):
            if self.command:
                self.command()

    class DummyTk(DummyWidget):
        def title(self, text):
            pass

        def after(self, ms, func):
            pass

        def protocol(self, name, func):
            pass

        def mainloop(self):
            pass

        def destroy(self):
            pass

    class DummyToplevel(DummyTk):
        def overrideredirect(self, flag):
            pass

        def attributes(self, *args, **kwargs):
            pass

        def geometry(self, spec):
            pass

        def lift(self):
            pass

    class DummyCanvas(DummyWidget):
        def create_rectangle(self, *args, **kwargs):
            pass

    class DummyStringVar:
        def __init__(self, value=""):
            self.value = value

        def set(self, value: str) -> None:
            self.value = value

        def get(self) -> str:
            return self.value

    dummy_tk = SimpleNamespace(
        Tk=DummyTk,
        Button=DummyWidget,
        Label=DummyWidget,
        StringVar=DummyStringVar,
        Canvas=DummyCanvas,
        Toplevel=DummyToplevel,
        BOTH="both",
    )

    def dummy_select_region() -> Region:
        calls["count"] += 1
        return Region(1, 2, 3, 4)

    class DummyLogger:
        def __init__(self, path):
            pass

        def log(self, *args, **kwargs):
            pass

        def close(self):
            pass

    monkeypatch.setattr("quiz_automation.gui.tk", dummy_tk)
    monkeypatch.setattr("quiz_automation.gui.Watcher", DummyWatcher)
    monkeypatch.setattr("quiz_automation.gui.select_region", dummy_select_region)
    monkeypatch.setattr("quiz_automation.gui.QuizLogger", DummyLogger)
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.OpenAI", lambda api_key: SimpleNamespace()
    )
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_api_key", "test-key"
    )

    gui = QuizGUI()
    gui.select_btn.invoke()
    assert calls["count"] == 1
    assert gui.region == Region(1, 2, 3, 4)
    gui.start()
    gui.stop()
    assert calls["count"] == 1
