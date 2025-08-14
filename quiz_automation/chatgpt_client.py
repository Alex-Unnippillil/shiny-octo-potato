"""Client wrapper for the OpenAI API used by the quiz automation."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace

from openai import OpenAI

from .config import Settings, get_settings
from .utils import hash_text

settings = get_settings()


class ChatGPTResponse:
    """Response returned by :class:`ChatGPTClient`."""

    def __init__(
        self, answer: str, usage: SimpleNamespace | None, cost: float
    ) -> None:
        self.answer = answer
        self.usage = usage
        self.cost = cost

    def __iter__(self):  # pragma: no cover - simple iteration helper
        yield self.answer
        yield self.usage
        yield self.cost

    def __eq__(self, other: object) -> bool:  # pragma: no cover - trivial
        if isinstance(other, str):
            return self.answer == other
        return tuple(self) == other

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"ChatGPTResponse(answer={self.answer!r}, usage={self.usage!r}, "
            f"cost={self.cost!r})"
        )


CACHE: dict[str, ChatGPTResponse] = {}


class ChatGPTClient:
    """Small wrapper around OpenAI's client with basic caching and retries."""

    def __init__(self, config: Settings | None = None) -> None:
        self.settings = config or settings
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def ask(self, question: str) -> ChatGPTResponse:
        """Send ``question`` to the API and return the parsed response."""

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
            except Exception:
                if attempt == 2:
                    return ChatGPTResponse(
                        "Error: API request failed", None, 0.0
                    )
            else:
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
                    CACHE[key] = resp
                    return resp
                except Exception:
                    return ChatGPTResponse(
                        "Error: malformed response", None, 0.0
                    )

            time.sleep(backoff)
            backoff *= 2

        return ChatGPTResponse("Error: API request failed", None, 0.0)

