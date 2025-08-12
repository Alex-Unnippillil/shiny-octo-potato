"""Tkinter based GUI for quiz automation."""

from __future__ import annotations

import queue
import tkinter as tk
from typing import Optional

from .config import get_settings
from .watcher import Watcher
from .region_selector import Region, select_region


class QuizGUI:
    """Minimal GUI with Start and Stop controls."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Quiz Automation")
        self.status_var = tk.StringVar(value="Idle")
        self.event_queue: "queue.Queue[str]" = queue.Queue()
        self.watcher: Optional[Watcher] = None
        self.region: Optional[Region] = None
        self.settings = get_settings()

        start_btn = tk.Button(self.root, text="Start", command=self.start)
        start_btn.pack()
        stop_btn = tk.Button(self.root, text="Stop", command=self.stop)
        stop_btn.pack()
        tk.Label(self.root, textvariable=self.status_var).pack()
        self.root.after(100, self.process_events)

    def start(self) -> None:
        """Start the watcher thread."""
        if self.watcher is None:
            if self.region is None:
                self.region = select_region()
            self.watcher = Watcher(
                self.region.as_tuple(), self.on_question, self.settings.poll_interval
            )
            self.watcher.start()
            self.status_var.set("Running")

    def stop(self) -> None:
        """Stop the watcher thread."""
        if self.watcher:
            self.watcher.stop_flag.set()
            self.watcher.join()
            self.watcher = None
            self.status_var.set("Stopped")

    def on_question(self, text: str) -> None:
        self.event_queue.put(text)

    def process_events(self) -> None:
        try:
            text = self.event_queue.get_nowait()
            self.status_var.set(text)
        except queue.Empty:
            pass
        self.root.after(100, self.process_events)

    def run(self) -> None:
        self.root.mainloop()
