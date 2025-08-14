"""Utilities for monitoring a region of the screen and extracting text."""

from __future__ import annotations

import logging
from pathlib import Path
from threading import Event, Thread
from typing import Any, Callable, Tuple

import time
from mss import mss
from PIL import Image
import pytesseract


def _capture(region: Tuple[int, int, int, int]) -> Image.Image:
    """Capture a screenshot of ``region`` using :mod:`mss`."""

    left, top, width, height = region
    monitor = {"left": left, "top": top, "width": width, "height": height}
    with mss() as sct:
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.rgb)


def _ocr(img: Any) -> str:
    """Return OCR text for ``img`` using :mod:`pytesseract`."""

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
        super().__init__(daemon=True)
        self.region = region
        self.on_question = on_question
        self.poll_interval = poll_interval
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else None
        self.capture = capture or _capture
        self.ocr = ocr or _ocr
        self.on_error = on_error
        self.stop_flag = Event()
        self._last_text = ""

    def is_new_question(self, text: str) -> bool:
        """Return ``True`` if ``text`` differs from the last seen question."""

        return text != "" and text != self._last_text

    def run(self) -> None:  # pragma: no cover - tested via integration
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
                self.on_question(text)

            self.stop_flag.wait(self.poll_interval)

