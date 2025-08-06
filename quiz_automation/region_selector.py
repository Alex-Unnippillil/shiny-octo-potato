"""Utilities for selecting, saving, and loading a screen region."""
from __future__ import annotations

import json
import os
import sys
from typing import Tuple

try:  # pragma: no cover - optional dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    import pyautogui_stub as pyautogui  # type: ignore

Region = Tuple[int, int, int, int]
Point = Tuple[int, int]
CONFIG_PATH = "region.json"


def select_region() -> Tuple[Region, Point]:  # pragma: no cover - interactive
    """Interactively select a region and the base click point.

    The user is asked to position the mouse at the top-left and bottom-right
    corners of the quiz area, then at the centre of the first answer option.
    The coordinates are read via ``pyautogui.position`` and returned.
    """

    print("Move mouse to TOP-LEFT of quiz area and press Enter...")
    input()
    x1, y1 = pyautogui.position()
    print("Move mouse to BOTTOM-RIGHT of quiz area and press Enter...")
    input()
    x2, y2 = pyautogui.position()
    print("Move mouse to centre of answer A and press Enter...")
    input()
    bx, by = pyautogui.position()
    region: Region = (x1, y1, x2 - x1, y2 - y1)
    base: Point = (bx, by)
    return region, base


def save_region(region: Region, base: Point, path: str = CONFIG_PATH) -> None:
    """Persist the region and base point to ``path`` as JSON."""

    data = {"region": region, "base": base}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


def load_region(path: str = CONFIG_PATH) -> Tuple[Region, Point]:
    """Load region and base point from disk or fall back to defaults.

    If the configuration file does not exist and the process is running in an
    interactive TTY session, the user is prompted to select a region.  In
    non-interactive environments (such as automated tests) a default region of
    ``(0, 0, 100, 100)`` and base point ``(0, 0)`` is returned.
    """

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        region = tuple(data.get("region", (0, 0, 100, 100)))
        base = tuple(data.get("base", (0, 0)))
        return region, base  # type: ignore[return-value]

    if sys.stdin.isatty():  # interactive session
        region, base = select_region()
        save_region(region, base, path)
        return region, base

    # Non-interactive fallback for tests
    return (0, 0, 100, 100), (0, 0)
