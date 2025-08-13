"""Client wrapper for the OpenAI API used by the quiz automation."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace

from openai import OpenAI

from .config import Settings, get_settings



settings = get_settings()


class ChatGPTClient:


        settings = settings or globals()["settings"]
        if not settings.openai_api_key:
            raise ValueError("API key is required")
        self.client = client or OpenAI(api_key=settings.openai_api_key)
        self.settings = settings

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

                if attempt == 2:
                    return "Error: API request failed", None, 0.0
                time.sleep(backoff)
                backoff *= 2


