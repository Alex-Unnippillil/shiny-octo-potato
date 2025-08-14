"""Client wrapper for the OpenAI API used by the quiz automation."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace
from typing import Tuple

from openai import OpenAI

from .config import Settings, get_settings
from .utils import hash_text


settings: Settings = get_settings()
CACHE: dict[str, Tuple[str, SimpleNamespace | None, float]] = {}


class ChatGPTClient:
    """Small helper around the OpenAI responses API."""

    def __init__(self, cfg: Settings | None = None) -> None:
        self.settings = cfg or settings
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = OpenAI(self.settings.openai_api_key)

    def ask(self, question: str) -> tuple[str, SimpleNamespace | None, float]:
        """Ask ChatGPT a question and return the answer, usage and cost."""
        cache_key = hash_text(question)
        if cache_key in CACHE:
            return CACHE[cache_key]

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

                usage = getattr(completion, "usage", None)
                cost = 0.0
                if usage is not None:
                    cost = (
                        usage.input_tokens * self.settings.openai_input_cost
                        + usage.output_tokens * self.settings.openai_output_cost
                    ) / 1000

                CACHE[cache_key] = (answer, usage, cost)
                return answer, usage, cost
            except Exception:
                if attempt == 2:
                    return "Error: API request failed", None, 0.0
                time.sleep(backoff)
                backoff *= 2

        return "Error: API request failed", None, 0.0

