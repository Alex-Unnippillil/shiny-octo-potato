"""Minimal stubs for Pydantic features used in tests."""

from __future__ import annotations


def Field(default, **kwargs):  # noqa: D401 - simple stub
    """Return the provided default value."""
    return default


class BaseModel:
    def __init__(self, **data):
        for name, value in self.__class__.__dict__.items():
            if not name.startswith("__") and not callable(value):
                setattr(self, name, data.get(name, value))
