"""Simple Tkinter GUI for controlling the quiz automation."""
from __future__ import annotations

import queue
import time
import tkinter as tk
from typing import Any, Tuple

from .chatgpt_client import ChatGPTClient
from .clicker import click, compute_click
from .config import get_settings
from .logger import Logger
from .region_selector import load_region
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
        self.chat: ChatGPTClient | None = None
        self.logger: Logger | None = None
        self.base_point: Tuple[int, int] = (0, 0)

    def start(self) -> None:
        """Start the watcher thread and supporting services."""

        if self.watcher is None:
            region, self.base_point = load_region()
            self.chat = ChatGPTClient(self.cfg.openai_api_key)
            self.logger = Logger(self.cfg.db_path)
            self.watcher = Watcher(region, self.event_queue, self.cfg)
            self.watcher.start()
            self.root.after(100, self.process_events)
        self.status_var.set("Running")

    def process_events(self) -> None:
        """Process events emitted by the watcher thread."""

        try:
            while True:
                event, text, _img = self.event_queue.get_nowait()
                if event == "question":
                    self.handle_question(text)
        except queue.Empty:
            pass
        if self.watcher and not self.watcher.stop_flag.is_set():
            self.root.after(100, self.process_events)

    def handle_question(self, text: str) -> None:
        """Query ChatGPT, click the answer, and log the action."""

        if not self.chat or not self.logger:
            return
        answer = self.chat.ask(text)
        x, y = compute_click(self.base_point, answer)
        click((x, y))
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.logger.log(ts, text, answer, x, y)

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
