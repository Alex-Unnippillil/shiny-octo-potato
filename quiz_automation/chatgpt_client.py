"""Thin wrapper around OpenAI Chat Completions."""

from __future__ import annotations

import json
import time
from typing import Dict

from openai import OpenAI

from .config import get_settings
from .utils import hash_text

cache: Dict[str, str] = {}
settings = get_settings()


class ChatGPTClient:
    """Client for querying ChatGPT models."""

    def __init__(self, cache: Dict[str, str] | None = None) -> None:
        self.settings = settings
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.cache = cache if cache is not None else globals()["cache"]

    def ask(self, question: str) -> str:
        """Send question to model and return parsed answer letter."""
        qid = hash_text(question)
        if qid in self.cache:
            return self.cache[qid]
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
                    letter = data.get("answer", "")
                    self.cache[qid] = letter
                    return letter
                except (KeyError, IndexError, json.JSONDecodeError):
                    return "Error: malformed response"
            except Exception:  # pragma: no cover - depends on API failures
                if attempt == 2:
                    return "Error: API request failed"
                time.sleep(backoff)
                backoff *= 2
        return ""  # pragma: no cover
