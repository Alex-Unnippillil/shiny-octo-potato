"""Tkinter based GUI for quiz automation."""

from __future__ import annotations

import queue
from datetime import datetime
from pathlib import Path
import tkinter as tk


from .chatgpt_client import ChatGPTClient
from .clicker import click_answer
from .config import get_settings
from .logger import QuizLogger

from .region_selector import Region, select_region
from .watcher import Watcher


class QuizGUI:
    """Minimal GUI with Start and Stop controls."""

    def __init__(
        self,
        *,
        client: ChatGPTClient | None = None,
        logger: QuizLogger | None = None,
        click: Callable[[str, tuple[int, int, int, int]], tuple[int, int]] | None = None,
    ) -> None:
        self.settings = get_settings()
        self.client = client or ChatGPTClient()
        self.logger = logger or QuizLogger(Path("events.db"))
        self.click = click or click_answer

        self.root = tk.Tk()
        self.root.title("Quiz Automation")
        self.status_var = tk.StringVar(value="Idle")
        self.event_queue: "queue.Queue[str]" = queue.Queue()
        self.watcher: Optional[Watcher] = None
        self.region: Optional[Region] = None

        start_btn = tk.Button(self.root, text="Start", command=self.start)
        start_btn.pack()
        stop_btn = tk.Button(self.root, text="Stop", command=self.stop)
        stop_btn.pack()
        tk.Label(self.root, textvariable=self.status_var).pack()
        self.root.after(100, self.process_events)
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

    def start(self) -> None:
        """Start the watcher thread."""
        if self.watcher and self.watcher.is_alive():
            return
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
        if self.client is None:
            self.client = ChatGPTClient()
        answer = self.client.ask(text)
        if self.region is None:  # pragma: no cover - defensive
            return
        x, y = self.click(answer, self.region.as_tuple())
        ts = datetime.now().isoformat()
        self.logger.log(ts, text, answer, x, y)
        self.event_queue.put(f"{text} -> {answer}")

    def process_events(self) -> None:
        try:
            text = self.event_queue.get_nowait()
            self.status_var.set(text)
        except queue.Empty:
            pass
        self.root.after(100, self.process_events)

    def run(self) -> None:
        self.root.mainloop()

    def shutdown(self) -> None:
        self.stop()
        self.logger.close()
        self.root.destroy()
