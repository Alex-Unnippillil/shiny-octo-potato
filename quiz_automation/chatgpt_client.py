"""Thin wrapper around OpenAI Chat Completions."""

from __future__ import annotations

import json

import time

from openai import OpenAI

from .config import Settings, get_settings


# Module-level settings so tests can monkeypatch values before class instantiation.
# Only a single instance is created to avoid redundant initialization.
settings = get_settings()


class ChatGPTClient:
    """Client for querying ChatGPT models.

    This lightweight wrapper around the OpenAI client is primarily used by the
    quiz automation scripts. The constructor allows dependency injection of
    both the OpenAI client and runtime settings which simplifies testing.
    """

    def __init__(self, client: OpenAI | None = None, settings: Settings | None = None) -> None:
        """Initialize the client with optional dependencies.

        Parameters
        ----------
        client:
            Optional pre-configured :class:`OpenAI` instance. Supplying this
            allows dependency injection during testing.
        settings:
            Optional :class:`Settings` object. Defaults to the module-level
            ``settings`` instance. The ``ask`` method uses these settings and
            retries failed API requests with exponential backoff.

        Raises
        ------
        ValueError
            If ``openai_api_key`` is missing from the provided settings.
        """
        settings = settings or globals()["settings"]
        if not settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = client or OpenAI(api_key=settings.openai_api_key)
        self.settings = settings

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
            except Exception:  # pragma: no cover - depends on API failures
                if attempt == 2:
                    return "Error: API request failed"
                time.sleep(backoff)
                backoff *= 2
        return ""  # pragma: no cover
