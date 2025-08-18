import click
from pathlib import Path

from .logger import QuizLogger


@click.command("export-logs")
@click.option("--db", "db_path", type=click.Path(path_type=Path), default="events.db", show_default=True)
@click.option("--out", "out_path", type=click.Path(path_type=Path), required=True)
def export_logs(db_path: Path, out_path: Path) -> None:
    """Export all logged quiz events to a CSV file."""
    with QuizLogger(db_path) as logger:
        logger.export_csv(out_path)


if __name__ == "__main__":
    export_logs()
