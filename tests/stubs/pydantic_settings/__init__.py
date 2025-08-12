"""Minimal stub for pydantic_settings.BaseSettings."""

from __future__ import annotations

from pydantic import BaseModel as _BaseModel


class BaseSettings(_BaseModel):
    pass

