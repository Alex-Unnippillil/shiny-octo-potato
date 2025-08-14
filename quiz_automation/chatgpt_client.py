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

                if attempt == 2:
                    break
                time.sleep(backoff)
                backoff *= 2

        return "Error: API request failed", None, 0.0

