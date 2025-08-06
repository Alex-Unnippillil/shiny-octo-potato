from __future__ import annotations

import sqlite3

from quiz_automation.logger import Logger


def test_logger_inserts_record(tmp_path):
    db = tmp_path / "test.db"
    log = Logger(str(db))
    log.log("ts", "q", "a", 1, 2)
    row = sqlite3.connect(str(db)).execute("SELECT * FROM logs").fetchone()
    assert row == ("ts", "q", "a", 1, 2)
