"""OpenAI client wrapper used by the quiz automation project.

This module exposes a small helper class :class:`ChatGPTClient` that wraps the
``openai`` package.  It handles a couple of responsibilities:

* Validation and creation of the underlying :class:`~openai.OpenAI` client.
* Basic response caching keyed by a hash of the question text.
* Parsing the JSON payload returned by the model.
* Tracking token usage and estimating cost.

The main entry point is :meth:`ChatGPTClient.ask` which returns a
``ChatGPTResponse`` dataclass containing the generated answer, the usage object
returned by OpenAI and the calculated cost.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Dict

from openai import OpenAI

from .config import Settings, get_settings
from .utils import hash_text

settings = get_settings()


@dataclass
class ChatGPTResponse:
    """Response returned by :class:`ChatGPTClient`."""

    answer: str
    usage: SimpleNamespace | None
    cost: float

    def __iter__(self):  # pragma: no cover - convenience for tuple unpacking
        yield self.answer
        yield self.usage
        yield self.cost

    def __eq__(self, other: object) -> bool:  # pragma: no cover - trivial
        if isinstance(other, str):
            return self.answer == other
        return tuple(self) == other


class ChatGPTClient:
    """Small wrapper around OpenAI's client with basic caching and retries."""

    def __init__(
        self,
        client: OpenAI | None = None,
        cache: Dict[str, ChatGPTResponse] | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = client or OpenAI(api_key=self.settings.openai_api_key)
        self.cache: Dict[str, ChatGPTResponse] = cache or {}

    def ask(self, question: str) -> ChatGPTResponse:
        """Send ``question`` to the API and return the parsed response."""

        key = hash_text(question)
        if key in self.cache:
            return self.cache[key]

        prompt = f"Answer the quiz question with a single letter in JSON: {question}"

        backoff = 1.0
        for attempt in range(3):
            try:
                completion = self.client.responses.create(
                    model=self.settings.openai_model,
                    temperature=self.settings.openai_temperature,
                    input=prompt,
                )
            except Exception:
                if attempt == 2:
                    return ChatGPTResponse("Error: API request failed", None, 0.0)
                time.sleep(backoff)
                backoff *= 2.0
                continue

            try:
                text = completion.output[0].content[0].text
                data = json.loads(text)
                answer = data.get("answer", "")
                usage = getattr(completion, "usage", None)
                input_tokens = getattr(usage, "input_tokens", 0)
                output_tokens = getattr(usage, "output_tokens", 0)
                cost = (
                    input_tokens * self.settings.openai_input_cost
                    + output_tokens * self.settings.openai_output_cost
                ) / 1000
                resp = ChatGPTResponse(answer, usage, cost)
                self.cache[key] = resp
                return resp
            except Exception:
                return ChatGPTResponse("Error: malformed response", None, 0.0)

        return ChatGPTResponse("Error: API request failed", None, 0.0)

