"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Runtime settings for the quiz automation tool."""

    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini-high", env="OPENAI_MODEL")
    openai_temperature: float = Field(0.0, env="OPENAI_TEMPERATURE")
    poll_interval: float = Field(0.5, env="POLL_INTERVAL")
    screenshot_dir: Path | None = Field(None, env="SCREENSHOT_DIR")
    openai_input_cost: float = Field(0.0, env="OPENAI_INPUT_COST")
    openai_output_cost: float = Field(0.0, env="OPENAI_OUTPUT_COST")



def get_settings() -> Settings:
    """Return runtime configuration loaded from environment variables."""
    load_dotenv()
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini-high"),
        openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.0)),
        poll_interval=float(os.getenv("POLL_INTERVAL", 0.5)),
        screenshot_dir=Path(os.getenv("SCREENSHOT_DIR")) if os.getenv("SCREENSHOT_DIR") else None,
        openai_input_cost=float(os.getenv("OPENAI_INPUT_COST", 0.0)),
        openai_output_cost=float(os.getenv("OPENAI_OUTPUT_COST", 0.0)),

    )

