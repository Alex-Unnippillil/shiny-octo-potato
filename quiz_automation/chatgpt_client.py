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
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def ask(self, question: str) -> tuple[str, dict[str, int], float]:
        """Send question to model and return parsed answer letter, usage and cost."""
        prompt = f"Answer the quiz question with a single letter in JSON: {question}"
        backoff = 1.0
        for attempt in range(3):
            try:
                completion = self.client.responses.create(
                    model=self.settings.openai_model,
                    temperature=self.settings.openai_temperature,
                    input=prompt,
                )
                usage = {
                    "input_tokens": getattr(completion.usage, "input_tokens", 0),
                    "output_tokens": getattr(completion.usage, "output_tokens", 0),
                }
                cost = (
                    usage["input_tokens"] * self.settings.openai_input_cost
                    + usage["output_tokens"] * self.settings.openai_output_cost
                ) / 1000
                try:
                    data = json.loads(completion.output[0].content[0].text)
                    letter = data.get("answer", "")
                    return letter, usage, cost
                except (KeyError, IndexError, json.JSONDecodeError):
                    return "Error: malformed response", usage, cost
            except Exception:  # pragma: no cover - depends on API failures
                if attempt == 2:
                    return "Error: API request failed", {"input_tokens": 0, "output_tokens": 0}, 0.0
                time.sleep(backoff)
                backoff *= 2
        return "", {"input_tokens": 0, "output_tokens": 0}, 0.0  # pragma: no cover
