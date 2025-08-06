"""Application configuration loading using pydantic and python-dotenv."""
from __future__ import annotations

from pydantic import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    openai_api_key: str = ""
    poll_interval: float = 0.5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Load settings from the environment and return a Settings instance."""
    load_dotenv()
    return Settings()
