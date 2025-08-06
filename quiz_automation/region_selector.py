"""Utilities for selecting and storing a screen region."""
from __future__ import annotations

from typing import Tuple


def select_region() -> Tuple[int, int, int, int]:
    """Return a placeholder region.

    A real implementation would allow the user to draw a rectangle on the screen
    and persist the coordinates.
    """

    return (0, 0, 100, 100)
