"""Utilities for selecting the quiz capture region."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pyautogui
import tkinter as tk


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
    """Display a full-screen overlay allowing the user to drag out a region.

    A translucent Tk window is shown over the entire screen. The user clicks and
    drags to draw a rectangle representing the desired capture region. When the
    mouse button is released a :class:`Region` describing the rectangle is
    returned.
    """

    # Determine the size of the current screen using pyautogui so the overlay
    # covers the whole area.
    screen_w, screen_h = pyautogui.size()

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.3)
    root.geometry(f"{screen_w}x{screen_h}+0+0")

    canvas = tk.Canvas(root, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)

    start_x = start_y = 0
    selection = {"region": Region(0, 0, 0, 0)}

    def on_press(event: tk.Event) -> None:
        """Remember the starting mouse position and draw the rectangle."""
        nonlocal start_x, start_y
        start_x, start_y = pyautogui.position()
        canvas.delete("rect")
        canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", tags="rect")

    def on_drag(event: tk.Event) -> None:
        """Update the rectangle as the mouse moves."""
        current_x, current_y = pyautogui.position()
        canvas.coords("rect", start_x, start_y, current_x, current_y)

    def on_release(event: tk.Event) -> None:
        """Finalize region and exit the overlay."""
        end_x, end_y = pyautogui.position()
        left = min(start_x, end_x)
        top = min(start_y, end_y)
        width = abs(end_x - start_x)
        height = abs(end_y - start_y)
        selection["region"] = Region(left, top, width, height)
        root.quit()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    root.mainloop()
    root.destroy()
    return selection["region"]
