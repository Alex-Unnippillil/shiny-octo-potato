"""Minimal stub of Pydantic BaseModel."""

from __future__ import annotations


class BaseModel:
    def __init__(self, **data):
        for name, value in self.__class__.__dict__.items():
            if not name.startswith("__") and not callable(value):
                setattr(self, name, data.get(name, value))
