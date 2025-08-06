"""Screenshot capture and OCR watcher."""

from __future__ import annotations

from threading import Event, Thread
from typing import Callable, Tuple
import time


class Watcher(Thread):
    """Background thread that captures a region and performs OCR."""

    def __init__(self, region: Tuple[int, int, int, int], on_question: Callable[[str], None], poll_interval: float = 0.5) -> None:
        super().__init__(daemon=True)
        self.region = region
        self.on_question = on_question
        self.poll_interval = poll_interval
        self.stop_flag = Event()
        self._last_text = ""

    def capture(self):  # pragma: no cover - to be mocked
        """Capture screenshot of region."""
        raise NotImplementedError

    def ocr(self, img):  # pragma: no cover - to be mocked
        """Run OCR on image."""
        raise NotImplementedError

    def is_new_question(self, text: str) -> bool:
        """Check whether text differs from last captured question."""
        return text != "" and text != self._last_text

    def run(self) -> None:
        while not self.stop_flag.is_set():
            img = self.capture()
            text = self.ocr(img)
            if self.is_new_question(text):
                self._last_text = text
                self.on_question(text)
            time.sleep(self.poll_interval)
