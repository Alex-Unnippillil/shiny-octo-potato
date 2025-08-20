from types import SimpleNamespace
from threading import Event, Thread
from pathlib import Path
import json
import time

from quiz_automation.chatgpt_client import ChatGPTResponse
import quiz_automation.cli as cli


class DummyWatcher(Thread):
    def __init__(self, region, on_question, poll_interval, **kwargs):
        super().__init__(daemon=True)
        self.region = region
        self.on_question = on_question
        self.stop_flag = Event()

    def run(self) -> None:
        self.on_question("What is 2+2?")


class DummyClient:
    def ask(self, question: str) -> ChatGPTResponse:
        usage = SimpleNamespace(input_tokens=1, output_tokens=1)
        return ChatGPTResponse("A", usage, 0.0)


class DummyLogger:
    def __init__(self, path: Path):
        self.closed = False
        LOGGERS.append(self)

    def log(self, *args, **kwargs):
        pass

    def close(self) -> None:
        self.closed = True


LOGGERS: list[DummyLogger] = []


def _setup(monkeypatch):
    monkeypatch.setattr(cli, "Watcher", DummyWatcher)
    monkeypatch.setattr(cli, "ChatGPTClient", lambda: DummyClient())
    monkeypatch.setattr(cli, "QuizLogger", DummyLogger)
    monkeypatch.setattr(
        cli, "get_settings", lambda: SimpleNamespace(poll_interval=0.1, screenshot_dir=None)
    )
    real_sleep = time.sleep

    def fake_sleep(_):
        real_sleep(0.01)
        raise KeyboardInterrupt

    monkeypatch.setattr(cli.time, "sleep", fake_sleep)


def test_run_headless_with_region(monkeypatch, capsys):
    _setup(monkeypatch)
    cli.run_headless(["--region", "0", "0", "1", "1"])
    out = capsys.readouterr().out.strip()
    assert out == "What is 2+2? -> A"
    assert LOGGERS and LOGGERS[0].closed


def test_run_headless_with_config(monkeypatch, capsys, tmp_path):
    _setup(monkeypatch)
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps([0, 0, 1, 1]))
    cli.run_headless(["--config", str(cfg)])
    out = capsys.readouterr().out.strip()
    assert out == "What is 2+2? -> A"
    assert LOGGERS and LOGGERS[-1].closed
