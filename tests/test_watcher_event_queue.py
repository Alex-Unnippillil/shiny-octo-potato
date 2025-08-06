from __future__ import annotations

import queue
from types import SimpleNamespace

from quiz_automation.watcher import Watcher


def test_watcher_emits_event(monkeypatch):
    cfg = SimpleNamespace(poll_interval=0)
    q: "queue.Queue" = queue.Queue()
    w = Watcher((0, 0, 0, 0), q, cfg)

    def capture():
        w.stop_flag.set()
        return b"img"

    monkeypatch.setattr(w, "capture", capture)
    monkeypatch.setattr(w, "ocr", lambda _: "Q1")
    w.run()
    assert q.get_nowait()[0] == "question"
