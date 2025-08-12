"""Mouse automation utilities."""

from __future__ import annotations

from typing import Dict, Tuple, Optional

import pyautogui


LETTER_OFFSETS: Dict[str, int] = {"A": 0, "B": 1, "C": 2, "D": 3}


def _generate_offsets(num_options: int) -> Dict[str, int]:
    """Generate a mapping of letter to row index."""
    return {chr(ord("A") + i): i for i in range(num_options)}


def click_answer(
    letter: str,
    region: Tuple[int, int, int, int],
    *,
    offsets_map: Optional[Dict[str, int]] = None,
    num_options: Optional[int] = None,
) -> Tuple[int, int]:
    """Click within the region based on answer letter.

    Returns the coordinates clicked so tests can verify them.

    Either ``offsets_map`` or ``num_options`` can be supplied to support
    quizzes with differing numbers of options.
    """
    offsets = offsets_map
    if offsets is None:
        if num_options is None:
            offsets = LETTER_OFFSETS
        else:
            offsets = _generate_offsets(num_options)

    if letter not in offsets:
        raise ValueError(f"Unknown letter: {letter}")

    left, top, width, height = region
    row_height = height // len(offsets)
    y = top + offsets[letter] * row_height + row_height // 2
    x = left + width // 2
    pyautogui.click(x, y)
    return x, y
