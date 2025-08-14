"""Simplified watcher implementation for tests."""

from __future__ import annotations

from threading import Event, Thread
from typing import Any, Callable, Tuple


class Watcher(Thread):
    """Background thread that captures a region and performs OCR."""

    def __init__(
        self,
        region: Tuple[int, int, int, int],
        on_question: Callable[[str], None],
        poll_interval: float = 0.5,
        screenshot_dir=None,
        capture: Callable[[Tuple[int, int, int, int]], Any] | None = None,
        ocr: Callable[[Any], str] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        super().__init__(daemon=True)
        self.region = region
        self.on_question = on_question
        self.poll_interval = poll_interval
        self.capture = capture or (lambda r: None)
        self.ocr = ocr or (lambda img: "")
        self.on_error = on_error
        self.stop_flag = Event()
        self._last_text = ""

    def is_new_question(self, text: str) -> bool:
        """Return True if ``text`` is different from the last value."""

        if text and text != self._last_text:
            return True
        return False

    def run(self) -> None:  # pragma: no cover - thread loop stub
        pass
