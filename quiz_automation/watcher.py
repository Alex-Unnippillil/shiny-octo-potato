"""Screen watcher that captures a region and performs OCR."""
from __future__ import annotations

import queue
import time
from threading import Event, Thread
from typing import Any, Optional, Tuple

try:  # pragma: no cover - optional dependency
    from mss import mss
except Exception:  # pragma: no cover
    mss = None  # type: ignore


class Watcher(Thread):
    """Thread that watches a screen region for new quiz questions."""

    def __init__(
        self, region: Tuple[int, int, int, int], event_queue: "queue.Queue[Any]", cfg: Any
    ) -> None:
        super().__init__(daemon=True)
        self.region = region
        self.event_queue = event_queue
        self.cfg = cfg
        self.stop_flag = Event()
        self.last_question: Optional[str] = None
        self.sct = mss() if mss else None

    # Placeholder methods to be replaced with real implementations
    def capture(self) -> bytes:  # pragma: no cover - to be mocked in tests
        """Capture the screen region and return raw image bytes."""

        if self.sct:
            left, top, width, height = self.region
            img = self.sct.grab({"left": left, "top": top, "width": width, "height": height})
            return img.rgb  # type: ignore[return-value]
        return b""

    def ocr(self, img: bytes) -> str:  # pragma: no cover - to be mocked in tests
        """Perform OCR on the given image and return detected text."""

        return "Sample Question?"

    def is_new_question(self, text: str) -> bool:
        """Determine whether the OCR text represents a new question."""

        if text and text != self.last_question:
            self.last_question = text
            return True
        return False

    def run(self) -> None:  # pragma: no cover - thread loop
        """Start the watcher loop."""

        while not self.stop_flag.is_set():
            img = self.capture()
            text = self.ocr(img)
            if self.is_new_question(text):
                self.event_queue.put(("question", text, img))
            time.sleep(self.cfg.poll_interval)
