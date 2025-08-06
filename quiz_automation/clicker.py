"""Click utilities for selecting answers."""
from __future__ import annotations

from typing import Dict, Tuple

import pyautogui

LETTER_OFFSETS: Dict[str, int] = {"A": 0, "B": 40, "C": 80, "D": 120}


def compute_click(base: Tuple[int, int], letter: str) -> Tuple[int, int]:
    """Return the absolute coordinates for the given answer letter."""

    x, y = base
    offset = LETTER_OFFSETS[letter.upper()]
    return x, y + offset


def click(point: Tuple[int, int]) -> None:  # pragma: no cover - interacts with GUI
    """Perform the mouse click at the given point."""

    pyautogui.click(*point)
