from pathlib import Path
import sqlite3
import pytest

from quiz_automation.logger import QuizLogger


def test_logger_inserts(tmp_path: Path):
    db_path = tmp_path / "events.db"
    with QuizLogger(db_path) as logger:
        logger.log("ts", "question", "A", 1, 2, 3, 4, 5.5)
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT * FROM events").fetchone()
    assert row == ("ts", "question", "A", 1, 2, 3, 4, 5.5)


def test_logger_closes_connection(tmp_path: Path):
    db_path = tmp_path / "events.db"
    with QuizLogger(db_path) as logger:
        logger.log("ts", "question", "A", 1, 2, 3, 4, 5.5)
    with pytest.raises(sqlite3.ProgrammingError):
        logger.conn.execute("SELECT 1")
