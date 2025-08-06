from pathlib import Path
import sqlite3

from quiz_automation.logger import QuizLogger


def test_logger_inserts(tmp_path: Path):
    db_path = tmp_path / "events.db"
    logger = QuizLogger(db_path)
    logger.log("ts", "question", "A", 1, 2)
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT * FROM events").fetchone()
    assert row == ("ts", "question", "A", 1, 2)
