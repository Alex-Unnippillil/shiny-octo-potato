"""Fallback stub for pydantic.BaseSettings."""
from __future__ import annotations

import os
from typing import Any


class BaseSettings:  # pragma: no cover - simple stub
    """Very small subset of ``pydantic.BaseSettings`` used in tests."""

    def __init__(self, **data: Any) -> None:
        for field in self.__annotations__:
            env_name = field.upper()
            if env_name in os.environ:
                setattr(self, field, os.environ[env_name])
        for key, value in data.items():
            setattr(self, key, value)
