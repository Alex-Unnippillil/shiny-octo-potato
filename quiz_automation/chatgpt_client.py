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

settings = get_settings()
CACHE: Dict[str, str] = {}




    Parameters
    ----------
    client:

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


        Returns
        -------
        tuple

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

      
