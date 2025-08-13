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
        """Initialize the client with API key and settings."""
        self.settings = settings or globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = client or OpenAI(api_key=self.settings.openai_api_key)

    def ask(self, question: str) -> tuple[str, dict[str, int], float]:
        """Send question to model and return answer, usage and cost.

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
                input_tokens = getattr(getattr(completion, "usage", object()), "input_tokens", 0)
                output_tokens = getattr(getattr(completion, "usage", object()), "output_tokens", 0)
                usage = {"input_tokens": input_tokens, "output_tokens": output_tokens}
                cost = (
                    input_tokens * self.settings.openai_input_cost
                    + output_tokens * self.settings.openai_output_cost
                ) / 1000.0
                try:
                    data = json.loads(completion.output[0].content[0].text)
                    answer = data.get("answer", "")
                except (KeyError, IndexError, json.JSONDecodeError):
                    return "Error: malformed response", usage, cost
                return answer, usage, cost
            except Exception:  # pragma: no cover - depends on API failures
                if attempt == 2:
                    return "Error: API request failed", {"input_tokens": 0, "output_tokens": 0}, 0.0
                time.sleep(backoff)
                backoff *= 2
        return "", {"input_tokens": 0, "output_tokens": 0}, 0.0  # pragma: no cover
