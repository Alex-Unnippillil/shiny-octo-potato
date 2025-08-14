"""Client wrapper for the OpenAI API used by the quiz automation."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace
from typing import Dict, Tuple

from openai import OpenAI

from .config import Settings, get_settings
from .utils import hash_text

settings = get_settings()
CACHE: Dict[str, str] = {}


class ChatGPTClient:
    """Minimal wrapper around OpenAI's Responses API.

    Parameters
    ----------
    client:
        Optional pre-configured :class:`OpenAI` client instance.
    cache:
        Mutable mapping used to store question/answer pairs.
    settings:
        Runtime configuration. Defaults to module-level ``settings``.
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        cache: Dict[str, str] | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = client or OpenAI(api_key=self.settings.openai_api_key)
        self.cache = cache or CACHE

    def ask(self, question: str) -> Tuple[str, SimpleNamespace | None, float]:
        """Send ``question`` to OpenAI and return the parsed answer.

        The method caches answers by the hash of ``question``. On subsequent
        calls with the same question the cached answer is returned and the
        usage and cost values are ``None`` and ``0.0`` respectively.

        Returns
        -------
        tuple
            ``(answer, usage, cost)`` where ``answer`` is the extracted
            single-letter response, ``usage`` is the token usage object from
            OpenAI (or ``None`` when unavailable) and ``cost`` is the estimated
            dollar cost of the request.
        """

        qid = hash_text(question)
        if qid in self.cache:
            return self.cache[qid], None, 0.0

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
                    in_cost = getattr(self.settings, "openai_input_cost", 0.0)
                    out_cost = getattr(self.settings, "openai_output_cost", 0.0)
                    cost = (
                        usage.input_tokens * in_cost
                        + usage.output_tokens * out_cost
                    ) / 1000
                self.cache[qid] = answer
                return answer, usage, cost
            except Exception:
                if attempt == 2:
                    return "Error: API request failed", None, 0.0
                time.sleep(backoff)
                backoff *= 2

        return "Error: API request failed", None, 0.0
