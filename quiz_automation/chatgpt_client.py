"""Thin wrapper around OpenAI Chat Completions."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace

from openai import OpenAI

from .config import Settings, get_settings


# Module-level settings so tests can monkeypatch values before class instantiation.
settings = get_settings()


class ChatGPTClient:
    """Client for querying ChatGPT models."""

    def __init__(self, client: OpenAI | None = None, settings: Settings | None = None) -> None:
        """Initialize the client and ensure an API key is provided."""

        # Use the module-level ``settings`` object so tests can monkeypatch values.
        self.settings = settings or globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = client or OpenAI(api_key=self.settings.openai_api_key)

    def ask(self, question: str) -> tuple[str, SimpleNamespace | None, float]:
        """Send question to model and return parsed answer, usage, and cost.

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
                    answer = data.get("answer", "")
                except (KeyError, IndexError, json.JSONDecodeError):
                    return "Error: malformed response", None, 0.0
                usage = getattr(
                    completion,
                    "usage",
                    SimpleNamespace(input_tokens=0, output_tokens=0),
                )
                cost = (
                    usage.input_tokens * self.settings.openai_input_cost
                    + usage.output_tokens * self.settings.openai_output_cost
                ) / 1000.0
                return answer, usage, cost
            except Exception:  # pragma: no cover - depends on API failures
                if attempt == 2:
                    return "Error: API request failed", None, 0.0
                time.sleep(backoff)
                backoff *= 2
        return "", None, 0.0  # pragma: no cover

