"""Simple Tkinter GUI for controlling the quiz automation."""
from __future__ import annotations

import queue
import tkinter as tk
from typing import Any

from .config import get_settings
from .watcher import Watcher


class QuizGUI:
    """Tkinter-based GUI providing Start and Stop controls."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Quiz Automation")
        self.event_queue: "queue.Queue[Any]" = queue.Queue()
        self.cfg = get_settings()

        self.status_var = tk.StringVar(value="Idle")
        tk.Label(self.root, textvariable=self.status_var).pack()
        tk.Button(self.root, text="Start", command=self.start).pack()
        tk.Button(self.root, text="Stop", command=self.stop).pack()

        self.watcher: Watcher | None = None

    def start(self) -> None:
        """Start the watcher thread."""

        if self.watcher is None:
            region = (0, 0, 100, 100)
            self.watcher = Watcher(region, self.event_queue, self.cfg)
            self.watcher.start()
        self.status_var.set("Running")

    def stop(self) -> None:
        """Stop the watcher thread."""

        if self.watcher is not None:
            self.watcher.stop_flag.set()
            self.watcher.join(timeout=1)
            self.watcher = None
        self.status_var.set("Stopped")

    def run(self) -> None:
        """Run the Tkinter event loop."""

        self.root.mainloop()
