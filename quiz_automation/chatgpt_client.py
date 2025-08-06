"""Thin wrapper around OpenAI Chat Completions."""

from __future__ import annotations

import json

from openai import OpenAI

from .config import settings


class ChatGPTClient:
    """Client for querying ChatGPT models."""

    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)

    def ask(self, question: str) -> str:
        """Send question to model and return parsed answer letter."""
        completion = self.client.responses.create(
            model="gpt-4o-mini-high",
            input=f"Answer the quiz question with a single letter in JSON: {question}",
        )
        data = json.loads(completion.output[0].content[0].text)
        return data.get("answer", "")
