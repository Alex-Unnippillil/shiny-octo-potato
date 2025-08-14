"""Client wrapper for the OpenAI API used by the quiz automation."""

from __future__ import annotations

import json
import time
from typing import Any

from openai import OpenAI

from .config import Settings, get_settings
from .utils import hash_text

# Module level settings object so tests can monkeypatch attributes.
settings = get_settings()

# Simple in-memory cache to avoid duplicate API calls during a session.
CACHE: dict[str, str] = {}


class ChatGPTClient:
    """Thin wrapper around the OpenAI Responses API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings if settings is not None else globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    # ------------------------------------------------------------------
    def ask(self, question: str):
        """Ask *question* and return the model's answer.

        If the same question was asked before, the cached answer is returned
        directly. Otherwise the OpenAI Responses API is queried. When usage
        information is available the tuple ``(answer, usage, cost)`` is
        returned. If not, only the answer string is returned. The ``cost`` is
        calculated from token counts using optional settings ``openai_input_cost``
        and ``openai_output_cost``.
        """

        key = hash_text(question)
        if key in CACHE:
            return CACHE[key]

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

                usage: Any | None = getattr(completion, "usage", None)
                cost = 0.0
                if usage is not None:
                    input_cost = getattr(self.settings, "openai_input_cost", 0.0)
                    output_cost = getattr(self.settings, "openai_output_cost", 0.0)
                    cost = (
                        usage.input_tokens * input_cost
                        + usage.output_tokens * output_cost
                    ) / 1000

                CACHE[key] = answer
                if usage is None:
                    return answer
                return answer, usage, cost
            except Exception:
                if attempt == 2:
                    return "Error: API request failed", None, 0.0
                time.sleep(backoff)
                backoff *= 2

        return "Error: API request failed", None, 0.0

