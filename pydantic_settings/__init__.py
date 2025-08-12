"""Minimal stand-in for pydantic-settings BaseSettings."""

from __future__ import annotations

import os

from pydantic import BaseModel


class BaseSettings(BaseModel):
    """Simplified settings loader using environment variables."""

    def __init__(self, **data):
        for name, field in self.model_fields.items():
            env_name = None
            if field.json_schema_extra:
                env_name = field.json_schema_extra.get("env")
            if env_name and env_name in os.environ:
                data.setdefault(name, os.environ[env_name])
        super().__init__(**data)

