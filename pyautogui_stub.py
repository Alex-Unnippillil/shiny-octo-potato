"""Minimal pyautogui stub for non-GUI environments."""
from __future__ import annotations

from typing import Tuple


def click(x: int, y: int) -> None:  # pragma: no cover - stub
    """Stub click function that does nothing."""

    return None


def position() -> Tuple[int, int]:  # pragma: no cover - stub
    """Return a fixed mouse position."""

    return (0, 0)
