import sqlite3
import sqlite3
from pathlib import Path

import pytest

from quiz_automation.logger import QuizLogger


def test_logger_inserts(tmp_path: Path):
    db_path = tmp_path / "events.db"
    with QuizLogger(db_path) as logger:
        logger.log("ts", "question", "A", 1, 2, 10, 5, 0.002)
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT * FROM events").fetchone()
    assert row == ("ts", "question", "A", 1, 2, 10, 5, 0.002)


def test_logger_migrates_existing_db(tmp_path: Path):
    db_path = tmp_path / "events.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE events (ts TEXT, question TEXT, answer TEXT, x INT, y INT)"
    )
    conn.commit()
    conn.close()

    with QuizLogger(db_path) as logger:
        logger.log("ts", "q", "B", 3, 4, 1, 1, 0.1)
    conn = sqlite3.connect(db_path)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(events)")]
    assert {"input_tokens", "output_tokens", "cost"}.issubset(cols)
    row = conn.execute("SELECT * FROM events").fetchone()
    assert row == ("ts", "q", "B", 3, 4, 1, 1, 0.1)


def test_logger_closes_connection(tmp_path: Path):
    db_path = tmp_path / "events.db"
    with QuizLogger(db_path) as logger:
        logger.log("ts", "question", "A", 1, 2, 0, 0, 0)
    with pytest.raises(sqlite3.ProgrammingError):
        logger.conn.execute("SELECT 1")
