"""Lightweight stub of pydantic's BaseSettings."""
from __future__ import annotations

import os
from typing import Any


class BaseSettings:
    """Very small subset of pydantic.BaseSettings for tests."""

    def __init__(self, **data: Any) -> None:
        for field in self.__annotations__:
            env_name = field.upper()
            if env_name in os.environ:
                setattr(self, field, os.environ[env_name])
        for key, value in data.items():
            setattr(self, key, value)
