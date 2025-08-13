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

    def __init__(
        self, client: OpenAI | None = None, settings: Settings | None = None
    ) -> None:
        """Initialize the client.

        Parameters
        ----------
        client:
            Optional pre-configured OpenAI client. If not provided, one will be
            created using the API key from the provided settings.
        settings:
            Optional runtime settings. Defaults to the module level ``settings``
            object which can be monkeypatched in tests.
        """
        self.settings = settings or globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = client or OpenAI(api_key=self.settings.openai_api_key)

    def ask(self, question: str):
        """Send question to model and return parsed answer and usage information.

        Returns a tuple of ``(answer, usage, cost)`` where ``usage`` is the
        token usage object returned by the OpenAI API and ``cost`` is the USD
        cost computed from the input and output tokens.
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
                usage = getattr(
                    completion,
                    "usage",
                    SimpleNamespace(input_tokens=0, output_tokens=0, total_tokens=0),
                )
                cost = (
                    usage.input_tokens / 1000 * self.settings.openai_input_cost
                    + usage.output_tokens / 1000 * self.settings.openai_output_cost
                )
                try:
                    data = json.loads(completion.output[0].content[0].text)
                    answer = data.get("answer", "")
                    return answer, usage, cost
                except (KeyError, IndexError, json.JSONDecodeError):
                    return "Error: malformed response", usage, cost
            except Exception:  # pragma: no cover - depends on API failures
                if attempt == 2:
                    usage = SimpleNamespace(
                        input_tokens=0, output_tokens=0, total_tokens=0
                    )
                    return "Error: API request failed", usage, 0.0
                time.sleep(backoff)
                backoff *= 2
        usage = SimpleNamespace(input_tokens=0, output_tokens=0, total_tokens=0)
        return "", usage, 0.0  # pragma: no cover
