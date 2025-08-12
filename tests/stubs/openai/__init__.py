"""Minimal stub for OpenAI client."""

from __future__ import annotations


class OpenAI:
    def __init__(self, api_key: str = "") -> None:  # pragma: no cover
        self.api_key = api_key
        self.responses = None
