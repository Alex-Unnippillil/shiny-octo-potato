"""Client wrapper for the OpenAI API used by the quiz automation."""

from __future__ import annotations

import json
import time
from typing import Any, Tuple

from openai import OpenAI

from .config import Settings, get_settings
from .utils import hash_text


settings = get_settings()
CACHE: dict[str, Tuple[str, Any, float]] = {}


class ChatGPTClient:
    """Lightweight client around the OpenAI API with basic caching."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def ask(self, question: str) -> Tuple[str, Any, float]:
        """Ask a question and return the answer, usage, and estimated cost."""
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
                    text = completion.output[0].content[0].text
                    data = json.loads(text)
                    answer = data.get("answer", "")
                except (KeyError, IndexError, json.JSONDecodeError):
                    return "Error: malformed response", None, 0.0

                usage = getattr(completion, "usage", None)
                input_tokens = getattr(usage, "input_tokens", 0)
                output_tokens = getattr(usage, "output_tokens", 0)
                cost = (
                    input_tokens * self.settings.openai_input_cost
                    + output_tokens * self.settings.openai_output_cost
                ) / 1000
                CACHE[key] = (answer, usage, cost)
                return answer, usage, cost
            except Exception:
                if attempt == 2:
                    return "Error: API request failed", None, 0.0
                time.sleep(backoff)
                backoff *= 2

