"""Fallback stub for the OpenAI client."""
from __future__ import annotations


class OpenAIError(Exception):
    """Generic OpenAI error stub."""


class OpenAI:
    """Minimal client exposing ``responses.create`` for tests."""

    def __init__(self, *_, **__):
        self.responses = None
