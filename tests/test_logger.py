from pathlib import Path
import csv
import sqlite3

import pytest
from click.testing import CliRunner

from quiz_automation.logger import QuizLogger
from quiz_automation.cli import export_logs


def test_logger_inserts(tmp_path: Path):
    db_path = tmp_path / "events.db"
    with QuizLogger(db_path) as logger:
        logger.log("ts", "question", "A", 1, 2, 3, 4, 0.5)
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT * FROM events").fetchone()
    assert row == ("ts", "question", "A", 1, 2, 3, 4, 0.5)
    assert row[5] == 3
    assert row[6] == 4
    assert row[7] == pytest.approx(0.5)


def test_logger_closes_connection(tmp_path: Path):
    db_path = tmp_path / "events.db"
    with QuizLogger(db_path) as logger:
        logger.log("ts", "question", "A", 1, 2, 3, 4, 0.5)
    with pytest.raises(sqlite3.ProgrammingError):
        logger.conn.execute("SELECT 1")


def test_export_csv(tmp_path: Path):
    db_path = tmp_path / "events.db"
    csv_path = tmp_path / "out.csv"
    with QuizLogger(db_path) as logger:
        logger.log("ts", "question", "A", 1, 2, 3, 4, 0.5)
        logger.export_csv(csv_path)
    with csv_path.open() as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == [
        "ts",
        "question",
        "answer",
        "x",
        "y",
        "input_tokens",
        "output_tokens",
        "cost",
    ]
    assert rows[1][0] == "ts"


def test_cli_export_logs(tmp_path: Path):
    db_path = tmp_path / "events.db"
    out_path = tmp_path / "out.csv"
    with QuizLogger(db_path) as logger:
        logger.log("ts", "question", "A", 1, 2, 3, 4, 0.5)
    runner = CliRunner()
    result = runner.invoke(export_logs, ["--db", str(db_path), "--out", str(out_path)])
    assert result.exit_code == 0, result.output
    with out_path.open() as fh:
        rows = list(csv.reader(fh))
    assert rows[1][0] == "ts"
