"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings for the quiz automation tool."""

    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    poll_interval: float = Field(0.5, env="POLL_INTERVAL")


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings()

