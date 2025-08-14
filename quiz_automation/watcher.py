"""Screenshot capture and OCR watcher."""

from __future__ import annotations

import logging

from pathlib import Path
from threading import Event, Thread
from typing import Any, Callable, Tuple

from mss import mss
from PIL import Image
import pytesseract
import time


def _capture(region: Tuple[int, int, int, int]) -> Image.Image:
    """Capture screenshot of the region using mss."""
    left, top, width, height = region
    monitor = {"left": left, "top": top, "width": width, "height": height}
    with mss() as sct:
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.rgb)


def _ocr(img: Any) -> str:
    """Run OCR on the image using pytesseract."""
    return pytesseract.image_to_string(img).strip()


class Watcher(Thread):
    """Background thread that captures a region and performs OCR."""

    def __init__(
        self,
        region: Tuple[int, int, int, int],
        on_question: Callable[[str], None],
        poll_interval: float = 0.5,
        screenshot_dir: Path | None = None,
        capture: Callable[[Tuple[int, int, int, int]], Any] | None = None,
        ocr: Callable[[Any], str] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Initialise the watcher thread.

        Args:
            region: Screen region to capture as ``(left, top, width, height)``.
            on_question: Callback invoked with new question text.
            poll_interval: Time in seconds between captures.
            screenshot_dir: Optional directory to save screenshots of new
                questions.
            capture: Function used to capture the screen region.
            ocr: Function used to extract text from an image.
            on_error: Callback invoked when ``capture`` or ``ocr`` raises an
                exception.
        """

        super().__init__(daemon=True)
        self.region: Tuple[int, int, int, int] = region
        self.on_question = on_question
        self.poll_interval = poll_interval
        self.capture = capture or _capture
        self.ocr = ocr or _ocr
        self.on_error = on_error
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else None
        self.stop_flag = Event()
        self._last_text = ""

    def is_new_question(self, text: str) -> bool:
        """Check whether text differs from the previously captured question."""
        return text != "" and text != self._last_text

    def run(self) -> None:
        """Main loop that captures, OCRs and notifies about new questions."""
        while not self.stop_flag.is_set():
            try:
                img = self.capture(self.region)
            except Exception as exc:  # pragma: no cover - logging behaviour
                logging.exception("Screenshot capture failed")
                if self.on_error:
                    self.on_error(exc)
                self.stop_flag.wait(self.poll_interval)
                continue

            try:
                text = self.ocr(img)
            except Exception as exc:  # pragma: no cover - logging behaviour
                logging.exception("OCR failed")
                if self.on_error:
                    self.on_error(exc)
                self.stop_flag.wait(self.poll_interval)
                continue

            if self.is_new_question(text):
                self._last_text = text
                if self.screenshot_dir:
                    try:
                        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
                        img.save(self.screenshot_dir / f"{int(time.time())}.png")
                    except Exception as exc:  # pragma: no cover - logging behaviour
                        logging.exception("Saving screenshot failed")
                        if self.on_error:
                            self.on_error(exc)
                self.on_question(text)

            self.stop_flag.wait(self.poll_interval)
