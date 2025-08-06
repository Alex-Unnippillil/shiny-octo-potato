"""Minimal stub of the OpenAI client for testing without network."""
from __future__ import annotations

from .error import OpenAIError

__all__ = ["OpenAI", "OpenAIError"]


class OpenAI:
    def __init__(self, *_, **__):
        self.responses = None

