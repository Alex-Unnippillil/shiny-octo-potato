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
                y INT,
                input_tokens INT,
                output_tokens INT,
                cost REAL
            )
            """
        )
        # Migration for databases created before token tracking existed
        cols = {row[1] for row in self.conn.execute("PRAGMA table_info(events)")}
        if "input_tokens" not in cols:
            self.conn.execute(
                "ALTER TABLE events ADD COLUMN input_tokens INT DEFAULT 0"
            )
        if "output_tokens" not in cols:
            self.conn.execute(
                "ALTER TABLE events ADD COLUMN output_tokens INT DEFAULT 0"
            )
        if "cost" not in cols:
            self.conn.execute("ALTER TABLE events ADD COLUMN cost REAL DEFAULT 0")
        self.conn.commit()

    def log(
        self,
        ts: str,
        question: str,
        answer: str,
        x: int,
        y: int,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO events (
                ts, question, answer, x, y, input_tokens, output_tokens, cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, question, answer, x, y, input_tokens, output_tokens, cost),
        )
        self.conn.commit()

    def close(self) -> None:
        """Close the underlying SQLite connection."""
        self.conn.close()

    def __enter__(self) -> "QuizLogger":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
