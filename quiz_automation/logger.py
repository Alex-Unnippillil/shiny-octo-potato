"""SQLite logger for quiz events."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class QuizLogger:
    """Persist events into SQLite database."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                ts TEXT,
                question TEXT,
                answer TEXT,
                x INT,
                y INT
            )
            """
        )
        self.conn.commit()

    def log(self, ts: str, question: str, answer: str, x: int, y: int) -> None:
        self.conn.execute(
            "INSERT INTO events (ts, question, answer, x, y) VALUES (?, ?, ?, ?, ?)",
            (ts, question, answer, x, y),
        )
        self.conn.commit()
