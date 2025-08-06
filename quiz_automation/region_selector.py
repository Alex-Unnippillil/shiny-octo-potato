"""Utilities for selecting the quiz capture region."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Region:
    """Screen region defined by top-left x/y and size."""

    left: int
    top: int
    width: int
    height: int

    def as_tuple(self) -> Tuple[int, int, int, int]:
        """Return region as tuple."""
        return self.left, self.top, self.width, self.height


def select_region() -> Region:
    """Placeholder region selector returning a default box."""
    return Region(0, 0, 100, 100)
