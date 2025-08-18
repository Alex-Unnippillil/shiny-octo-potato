from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

from .chatgpt_client import ChatGPTClient, ChatGPTResponse
from .config import get_settings
from .logger import QuizLogger
from .watcher import Watcher


RegionTuple = Tuple[int, int, int, int]


def _load_region(args: argparse.Namespace) -> RegionTuple:
    if args.region:
        return tuple(args.region)  # type: ignore[return-value]
    if args.config:
        data = json.loads(Path(args.config).read_text())
        if isinstance(data, dict):
            data = data.get("region", [])
        if not (isinstance(data, Iterable) and len(data) == 4):
            raise SystemExit("Invalid config file")
        return tuple(int(x) for x in data)  # type: ignore[return-value]
    raise SystemExit("Region not specified. Use --region or --config")


def run_headless(argv: list[str] | None = None) -> None:
    """Run quiz automation without a GUI."""

    parser = argparse.ArgumentParser(description="Headless quiz automation")
    parser.add_argument(
        "--region",
        nargs=4,
        type=int,
        metavar=("LEFT", "TOP", "WIDTH", "HEIGHT"),
        help="Capture region coordinates",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON file containing region coordinates",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("events.db"),
        help="Path to SQLite log database",
    )
    args = parser.parse_args(argv)

    region = _load_region(args)
    settings = get_settings()
    client = ChatGPTClient()
    logger = QuizLogger(args.db)

    def on_question(text: str) -> None:
        resp: ChatGPTResponse = client.ask(text)
        print(f"{text} -> {resp.answer}")
        ts = datetime.now().isoformat()
        input_tokens = getattr(resp.usage, "input_tokens", 0)
        output_tokens = getattr(resp.usage, "output_tokens", 0)
        logger.log(
            ts,
            text,
            resp.answer,
            0,
            0,
            input_tokens,
            output_tokens,
            resp.cost,
        )

    watcher = Watcher(
        region,
        on_question,
        settings.poll_interval,
        screenshot_dir=settings.screenshot_dir,
    )
    watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        watcher.stop_flag.set()
        watcher.join()
        logger.close()
