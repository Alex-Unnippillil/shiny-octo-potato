from __future__ import annotations

import queue
from types import SimpleNamespace

from quiz_automation.watcher import Watcher


def test_watcher_is_new_question():
    cfg = SimpleNamespace(poll_interval=0)
    q: "queue.Queue" = queue.Queue()
    w = Watcher((0, 0, 0, 0), q, cfg)
    assert w.is_new_question("Q1")
    assert not w.is_new_question("Q1")
