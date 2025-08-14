"""OpenAI client wrapper used by the quiz automation project.

This module exposes a small helper class :class:`ChatGPTClient` that wraps the
`openai` package.  It handles a couple of responsibilities:

* Validation and creation of the underlying :class:`~openai.OpenAI` client.
* Basic response caching keyed by a hash of the question text.
* Parsing the JSON payload returned by the model.
* Tracking token usage and estimating cost.

The main entry point is :meth:`ChatGPTClient.ask` which returns a tuple of the
generated answer, the usage object returned by OpenAI and the calculated cost.
"""

from __future__ import annotations

import json
import time
from typing import Dict, Tuple

from openai import OpenAI

from .config import Settings, get_settings
from .utils import hash_text

# Module level configuration and cache -------------------------------------

settings: Settings = get_settings()
"""Runtime configuration loaded from the environment."""

CACHE: Dict[str, str] = {}
"""Simple in-memory cache keyed by the hash of the question text."""


class ChatGPTClient:
    """Thin wrapper around :class:`~openai.OpenAI` with caching and retries."""

    def __init__(
        self,
        client: OpenAI | None = None,
        cache: Dict[str, str] | None = None,
        settings: Settings | None = None,
    ) -> None:
        """Initialise a new client instance.

        Parameters
        ----------
        client:
            Optional pre‑configured :class:`~openai.OpenAI` client.  When omitted
            a new instance is created using the API key from ``settings``.
        cache:
            Optional dictionary used for caching.  Falls back to the module
            level :data:`CACHE`.
        settings:
            Optional settings override.  If not provided the module level
            :data:`settings` object is used.

        Raises
        ------
        ValueError
            If the OpenAI API key is not provided.
        """

        self.settings = settings or globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")

        # Create the OpenAI client unless one was provided explicitly.
        self.client = client or OpenAI(api_key=self.settings.openai_api_key)
        self.cache = cache or CACHE

    # ------------------------------------------------------------------
    def ask(self, question: str) -> Tuple[str, object | None, float]:
        """Query the model and return ``(answer, usage, cost)``.

        The method performs a simple cache lookup before hitting the API.  It
        will retry failed requests up to three times using exponential
        backoff.  Responses are expected to be JSON objects containing an
        ``"answer"`` field.  If parsing fails ``("Error: malformed response",
        None, 0.0)`` is returned.
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
                    text = completion.output[0].content[0].text
                    data = json.loads(text)
                    answer = data.get("answer", "")
                    if not answer:
                        raise KeyError("answer")
                except (KeyError, IndexError, json.JSONDecodeError):
                    return "Error: malformed response", None, 0.0

                # Cache the successful answer
                self.cache[qid] = answer

                usage = getattr(completion, "usage", None)
                cost = 0.0
                if usage is not None:
                    in_tokens = getattr(usage, "input_tokens", 0)
                    out_tokens = getattr(usage, "output_tokens", 0)
                    in_cost = getattr(self.settings, "openai_input_cost", 0.0)
                    out_cost = getattr(self.settings, "openai_output_cost", 0.0)
                    cost = (in_tokens * in_cost + out_tokens * out_cost) / 1000.0

                return answer, usage, cost
            except Exception:  # pragma: no cover - thin wrapper around client
                if attempt == 2:
                    break
                time.sleep(backoff)
                backoff *= 2

        return "Error: API request failed", None, 0.0

