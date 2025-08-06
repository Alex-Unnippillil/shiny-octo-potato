"""Mouse automation utilities."""

from __future__ import annotations

from typing import Dict, Tuple

import pyautogui


LETTER_OFFSETS: Dict[str, int] = {"A": 0, "B": 1, "C": 2, "D": 3}


def click_answer(letter: str, region: Tuple[int, int, int, int]) -> Tuple[int, int]:
    """Click within the region based on answer letter.

    Returns the coordinates clicked so tests can verify them.
    """
    left, top, width, height = region
    row_height = height // 4
    y = top + LETTER_OFFSETS[letter] * row_height + row_height // 2
    x = left + width // 2
    pyautogui.click(x, y)
    return x, y
