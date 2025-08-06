"""Logging utilities for persisting quiz actions."""
from __future__ import annotations

import sqlite3


class Logger:
    """Simple SQLite-based logger."""

    def __init__(self, db_path: str) -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, question TEXT, answer TEXT, x INT, y INT)"
        )

    def log(self, ts: str, question: str, answer: str, x: int, y: int) -> None:
        """Insert a log record."""

        self.conn.execute(
            "INSERT INTO logs VALUES (?, ?, ?, ?, ?)", (ts, question, answer, x, y)
        )
        self.conn.commit()
