from types import SimpleNamespace

import openai  # noqa: F401  # ensure stub is loaded

from quiz_automation.gui import QuizGUI
from quiz_automation.region_selector import Region
from quiz_automation.chatgpt_client import ChatGPTResponse


def test_on_question_flow(monkeypatch):
    calls = {}

    class DummyClient:
        def __init__(self):
            pass

        def ask(self, question: str):  # noqa: D401
            calls['question'] = question
            usage = SimpleNamespace(input_tokens=1, output_tokens=2)
            return ChatGPTResponse('B', usage, 0.5)

    def dummy_click(letter, region, offsets_map=None, num_options=None):
        calls['click'] = (letter, region)
        return 10, 20

    class DummyLogger:
        def __init__(self, path):
            calls['path'] = str(path)

        def log(self, ts, question, answer, x, y, in_toks, out_toks, cost):
            calls['log'] = (ts, question, answer, x, y, in_toks, out_toks, cost)
            return cost

        def close(self):
            calls['closed'] = True

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

        def protocol(self, name, func):
            pass

        def mainloop(self):
            pass

        def destroy(self):
            pass

    class DummyStringVar:
        def __init__(self, value=""):
            self.value = value

        def set(self, value: str) -> None:
            self.value = value

        def get(self) -> str:
            return self.value

    class DummyDateTime:
        @staticmethod
        def now():
            class D:
                @staticmethod
                def isoformat():
                    return "TS"
            return D()

    dummy_tk = SimpleNamespace(
        Tk=DummyTk, Button=DummyWidget, Label=DummyWidget, StringVar=DummyStringVar
    )

    monkeypatch.setattr("quiz_automation.gui.ChatGPTClient", DummyClient)
    monkeypatch.setattr("quiz_automation.gui.click_answer", dummy_click)
    monkeypatch.setattr("quiz_automation.gui.QuizLogger", DummyLogger)
    monkeypatch.setattr("quiz_automation.gui.tk", dummy_tk)
    monkeypatch.setattr("quiz_automation.gui.datetime", DummyDateTime)

    gui = QuizGUI()
    gui.region = Region(0, 0, 50, 50)
    gui.on_question("What is 2+2?")

    assert calls['question'] == "What is 2+2?"
    assert calls['click'] == (
        'B',
        (0, 0, 50, 50),
    )
    assert calls['log'] == (
        "TS",
        "What is 2+2?",
        'B',
        10,
        20,
        1,
        2,
        0.5,
    )
    # ensure token accounting and cost are preserved
    assert calls['log'][5] == 1
    assert calls['log'][6] == 2
    assert calls['log'][7] == 0.5

    assert gui.total_cost == 0.5
    assert gui.status_var.get() == "Running – $0.50"

    gui.shutdown()
    assert calls['closed'] is True
