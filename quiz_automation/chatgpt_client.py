"""Thin OpenAI wrapper for asking quiz questions."""
from __future__ import annotations

import json
import time
from openai import OpenAI
from openai.error import OpenAIError


class ChatGPTClient:
    """Client that queries ChatGPT and returns a single-letter answer."""

    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.total_tokens = 0

    def ask(self, question: str) -> str:
        """Send a question to the model and return the letter answer."""

        system_prompt = (
            'You answer with a single letter A-D as JSON: {"answer":"A"}'
        )
        for _ in range(3):
            try:
                response = self.client.responses.create(
                    model="gpt-4o-mini-high",
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                    ],
                )
                content = response.output_text
                data = json.loads(content)
                self.total_tokens += getattr(response.usage, "total_tokens", 0)
                return data["answer"]
            except (OpenAIError, KeyError, json.JSONDecodeError):
                time.sleep(0.5)
        raise RuntimeError("Failed to obtain answer from ChatGPT")
