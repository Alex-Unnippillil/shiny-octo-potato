"""Thin wrapper around OpenAI Chat Completions."""

from __future__ import annotations

import json
import time

from openai import OpenAI

from .config import Settings, get_settings

# Module-level settings so tests can monkeypatch values before class instantiation.
settings = get_settings()


class ChatGPTClient:
    """Client for querying ChatGPT models.

    This lightweight wrapper around the OpenAI client is primarily used by the
    quiz automation scripts. The constructor allows dependency injection of
    both the OpenAI client and runtime settings which simplifies testing.
    """

    def __init__(self, client: OpenAI | None = None, settings: Settings | None = None) -> None:
        """Initialize the client."""
        self.settings = settings or globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = client or OpenAI(api_key=self.settings.openai_api_key)

    def ask(self, question: str) -> str:
        """Send question to model and return parsed answer letter.

        The request is retried up to three times with exponential backoff. If
        all attempts fail, an error string is returned instead of raising.
        """
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
            except Exception:
                if attempt == 2:
                    return "Error: API request failed"
                time.sleep(backoff)
                backoff *= 2
        return ""  # pragma: no cover
