"""Application configuration loading using pydantic and python-dotenv."""
from __future__ import annotations

try:  # pragma: no cover - optional dependency
    from pydantic import BaseSettings
except Exception:  # pragma: no cover
    from pydantic_stub import BaseSettings  # type: ignore

try:  # pragma: no cover - optional dependency
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    from dotenv_stub import load_dotenv  # type: ignore


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    openai_api_key: str = ""
    poll_interval: float = 0.5
    db_path: str = "quiz_log.sqlite"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Load settings from the environment and return a ``Settings`` instance."""

    load_dotenv()
    return Settings()
