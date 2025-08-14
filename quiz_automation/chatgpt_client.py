"""Client wrapper for the OpenAI API used by the quiz automation."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace

from openai import OpenAI

from .config import Settings, get_settings
from .utils import hash_text

settings = get_settings()
CACHE: dict[str, str] = {}


class ChatGPTClient:
    """Thin wrapper around the OpenAI client."""

    def __init__(
        self,
        settings: Settings | None = None,
        cache: dict[str, str] | None = None,
    ) -> None:
        self.settings = settings if settings is not None else globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.cache = CACHE if cache is None else cache

    def ask(self, question: str) -> tuple[str, SimpleNamespace | None, float]:
        """Return answer, usage and cost for *question*."""
        key = hash_text(question)
        if key in self.cache:
            return self.cache[key], None, 0.0

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
                    input_tokens = getattr(usage, "input_tokens", 0)
                    output_tokens = getattr(usage, "output_tokens", 0)
                    input_cost = getattr(self.settings, "openai_input_cost", 0.0)
                    output_cost = getattr(self.settings, "openai_output_cost", 0.0)
                    cost = (input_tokens * input_cost + output_tokens * output_cost) / 1000

                self.cache[key] = answer
                return answer, usage, cost
            except Exception:
                if attempt == 2:
                    return "Error: API request failed", None, 0.0
                time.sleep(backoff)
                backoff *= 2
        return "Error: API request failed", None, 0.0
