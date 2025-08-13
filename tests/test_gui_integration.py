from types import SimpleNamespace

from quiz_automation.gui import QuizGUI
from quiz_automation.region_selector import Region


def test_on_question_flow(monkeypatch):
    calls = {}

    class DummyClient:
        def __init__(self):
            pass

        def ask(self, question: str):
            calls['question'] = question
            return 'B', {'input_tokens': 10, 'output_tokens': 5}, 0.002

    def dummy_click(letter, region, offsets_map=None, num_options=None):
        calls['click'] = (letter, region)
        return 10, 20

    class DummyLogger:
        def __init__(self, path):
            calls['path'] = str(path)

        def log(self, ts, question, answer, x, y, input_tokens, output_tokens, cost):
            calls['log'] = (ts, question, answer, x, y, input_tokens, output_tokens, cost)

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
        10,
        5,
        0.002,
    )

    gui.shutdown()
    assert calls['closed'] is True
