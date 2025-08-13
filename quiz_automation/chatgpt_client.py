"""Thin wrapper around OpenAI Chat Completions."""

from __future__ import annotations

import json

import time

from openai import OpenAI

from .config import get_settings


settings = get_settings()


class ChatGPTClient:
    """Client for querying ChatGPT models."""

    def __init__(self) -> None:
        self.settings = settings
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = OpenAI(self.settings.openai_api_key)

    def ask(self, question: str) -> str:
        """Send question to model and return parsed answer letter."""
        prompt = f"Answer the quiz question with a single letter in JSON: {question}"
        backoff = 1.0
        for attempt in range(3):
            try:
                completion = self.client.responses.create(
                    model=self.settings.openai_model,
                    temperature=self.settings.openai_temperature,
                    input=prompt,
                )
                try:
                    data = json.loads(completion.output[0].content[0].text)
                    return data.get("answer", "")
                except (KeyError, IndexError, json.JSONDecodeError):
                    return "Error: malformed response"
            except Exception:  # pragma: no cover - depends on API failures
                if attempt == 2:
                    return "Error: API request failed"
                time.sleep(backoff)
                backoff *= 2
        return ""  # pragma: no cover
