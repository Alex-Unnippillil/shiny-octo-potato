"""Application configuration loaded from environment variables."""

from __future__ import annotations

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    """Runtime settings for the quiz automation tool."""

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini-high"
    openai_temperature: float = 0.0
    poll_interval: float = 0.5


settings = Settings()
