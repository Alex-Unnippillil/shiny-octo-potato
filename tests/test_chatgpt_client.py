from __future__ import annotations

from types import SimpleNamespace

from quiz_automation import chatgpt_client
from quiz_automation.chatgpt_client import ChatGPTClient


class DummyResponse:
    output_text = '{"answer": "C"}'

    class usage:
        total_tokens = 5


class DummyAPI:
    def __init__(self, *args, **kwargs):
        self.responses = SimpleNamespace(create=lambda **_: DummyResponse())


def test_chatgpt_client_parses_json(monkeypatch):
    monkeypatch.setattr(chatgpt_client, "OpenAI", lambda api_key: DummyAPI())
    client = ChatGPTClient("key")
    assert client.ask("Q?") == "C"
