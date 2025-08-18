"""SQLite logger for quiz events."""

from __future__ import annotations

import csv
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

    def export_csv(self, path: Path) -> None:
        """Dump all events rows to a CSV file at ``path``."""
        cursor = self.conn.execute("SELECT * FROM events")
        headers = [col[0] for col in cursor.description]
        with path.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)
            writer.writerows(cursor.fetchall())

    def close(self) -> None:
        """Close the underlying SQLite connection."""
        self.conn.close()

    def __enter__(self) -> "QuizLogger":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
