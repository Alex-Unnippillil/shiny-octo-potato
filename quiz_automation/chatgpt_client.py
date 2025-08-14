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




class ChatGPTClient:
    """Simple wrapper around OpenAI's API.

    Parameters
    ----------
    client:
        Optional preconfigured :class:`~openai.OpenAI` client.  When ``None`` a
        new client is created using the provided settings.
    cache:
        Optional dictionary used to cache answers keyed by the hash of the
        question text.  When ``None`` the module level ``CACHE`` is used.
    settings:
        Optional :class:`Settings` instance.  Defaults to module level
        ``settings``.
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
        self.cache = cache if cache is not None else CACHE

    def ask(self, question: str) -> Tuple[str, object | None, float]:
        """Ask ChatGPT a quiz question.

        Returns
        -------
        tuple
            ``(answer, usage, cost)`` where ``answer`` is the extracted answer
            from the response, ``usage`` is the token usage information or
            ``None`` if unavailable, and ``cost`` is the estimated cost in USD.
            In case of failure ``answer`` contains an error message and both
            ``usage`` and ``cost`` are ``None`` and ``0.0`` respectively.
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

                if attempt == 2:
                    break
                time.sleep(backoff)
                backoff *= 2

        return "Error: API request failed", None, 0.0

      
