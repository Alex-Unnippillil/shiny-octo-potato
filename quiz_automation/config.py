"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings for the quiz automation tool."""

    model_config = {"extra": "ignore"}

    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini-high", env="OPENAI_MODEL")
    openai_temperature: float = Field(0.0, env="OPENAI_TEMPERATURE")
    openai_input_cost: float = Field(0.0, env="OPENAI_INPUT_COST")
    openai_output_cost: float = Field(0.0, env="OPENAI_OUTPUT_COST")
    poll_interval: float = Field(0.5, env="POLL_INTERVAL")
    screenshot_dir: Path | None = Field(None, env="SCREENSHOT_DIR")



def get_settings() -> Settings:
    """Return runtime configuration loaded from environment variables."""

    load_dotenv()
    env_map = {
        "OPENAI_API_KEY": "openai_api_key",
        "OPENAI_MODEL": "openai_model",
        "OPENAI_TEMPERATURE": "openai_temperature",
        "OPENAI_INPUT_COST": "openai_input_cost",
        "OPENAI_OUTPUT_COST": "openai_output_cost",
        "POLL_INTERVAL": "poll_interval",
        "SCREENSHOT_DIR": "screenshot_dir",
    }
    data = {}
    for env_name, field in env_map.items():
        if env_name in os.environ:
            value = os.environ[env_name]
            if field in {
                "openai_temperature",
                "openai_input_cost",
                "openai_output_cost",
                "poll_interval",
            }:
                value = float(value)
            elif field == "screenshot_dir":
                value = Path(value)
            data[field] = value
    factory = getattr(Settings, "model_validate", None)
    if factory:
        return factory(data)
    return Settings(**data)

