"""Client wrapper for the OpenAI API used by the quiz automation."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace
from typing import Dict, Tuple

from openai import OpenAI

from .config import Settings, get_settings
from .utils import hash_text


# Module level settings and cache for reuse across instances.
settings: Settings = get_settings()
# Default cost attributes so monkeypatching in tests works even if the
# configuration does not provide them.
if not hasattr(settings, "openai_input_cost"):
    setattr(settings, "openai_input_cost", 0.0)
if not hasattr(settings, "openai_output_cost"):
    setattr(settings, "openai_output_cost", 0.0)

CACHE: Dict[str, str] = {}


class ChatGPTClient:
    """Wrapper around the OpenAI client with simple caching and cost tracking."""

    def __init__(
        self,
        client: OpenAI | None = None,
        cache: Dict[str, str] | None = None,
        settings: Settings | None = None,
    ) -> None:
        """Create a new :class:`ChatGPTClient` instance.

        Parameters
        ----------
        client:
            Optional pre-configured :class:`openai.OpenAI` client. If ``None`` a
            new client is created using the provided ``settings``.
        cache:
            Optional cache mapping question hashes to answers. A module level
            cache is used by default.
        settings:
            Optional application settings object. Defaults to module level
            ``settings``.

        Raises
        ------
        ValueError
            If no API key is available in the provided settings.
        """

        self.settings = settings or globals()["settings"]
        if not self.settings.openai_api_key:
            raise ValueError("API key is required")

        self.client = client or OpenAI(api_key=self.settings.openai_api_key)
        self.cache = cache if cache is not None else CACHE

    # ------------------------------------------------------------------
    def ask(self, question: str) -> Tuple[str, SimpleNamespace | None, float]:
        """Send ``question`` to the OpenAI API.

        The method first checks a local cache to avoid duplicate requests. On a
        cache hit the cached answer is returned with ``None`` usage information
        and zero cost. Otherwise the API is called up to three times with
        exponential backoff.

        Parameters
        ----------
        question:
            The quiz question to send to the model.

        Returns
        -------
        tuple
            A tuple ``(answer, usage, cost)`` where ``answer`` is the model's
            response, ``usage`` contains token statistics as provided by the API
            or ``None`` on cache hits, and ``cost`` is the estimated monetary
            cost of the request.
        """

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
                    if not answer:
                        raise KeyError
                except (KeyError, IndexError, json.JSONDecodeError):
                    return "Error: malformed response", None, 0.0

                self.cache[key] = answer

                usage = getattr(completion, "usage", None)
                cost = 0.0
                if usage is not None:
                    input_tokens = getattr(usage, "input_tokens", 0)
                    output_tokens = getattr(usage, "output_tokens", 0)
                    input_cost = getattr(self.settings, "openai_input_cost", 0.0)
                    output_cost = getattr(self.settings, "openai_output_cost", 0.0)
                    cost = (
                        input_tokens * input_cost + output_tokens * output_cost
                    ) / 1000

                return answer, usage, cost

            except Exception:  # pragma: no cover - error path
                if attempt == 2:
                    return "Error: API request failed", None, 0.0
                time.sleep(backoff)
                backoff *= 2

        # In practice this line is unreachable because the loop returns on the
        # last iteration when ``attempt == 2``.
        return "Error: API request failed", None, 0.0

