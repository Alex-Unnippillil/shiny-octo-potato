"""Screen watcher that captures a region and performs OCR."""
from __future__ import annotations

import queue
import time
from threading import Event, Thread
from typing import Any, Optional, Tuple

try:  # pragma: no cover - optional dependency
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from mss import mss
except Exception:  # pragma: no cover
    mss = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import cv2
    import numpy as np
    import pytesseract
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore
    np = None  # type: ignore
    pytesseract = None  # type: ignore


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

    def capture(self) -> Any:
        """Capture the screen region and return an image object."""

        if not self.sct or not Image:  # pragma: no cover - handled in tests
            return None
        left, top, width, height = self.region
        raw = self.sct.grab({"left": left, "top": top, "width": width, "height": height})
        return Image.frombytes("RGB", raw.size, raw.rgb)

    def preprocess(self, img: Any) -> Any:
        """Convert image to high-contrast grayscale using OpenCV."""

        if not (cv2 and np and Image) or img is None:  # pragma: no cover
            return img
        arr = np.array(img)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        thr = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return Image.fromarray(thr)

    def ocr(self, img: Any) -> str:
        """Perform OCR on the given image and return detected text."""

        if not pytesseract or img is None:  # pragma: no cover
            return ""
        processed = self.preprocess(img)
        text = pytesseract.image_to_string(processed, config="--oem 1 --psm 6")
        return text.strip()

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
