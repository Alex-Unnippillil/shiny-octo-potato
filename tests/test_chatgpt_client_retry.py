from __future__ import annotations

from types import SimpleNamespace

from quiz_automation import chatgpt_client
from quiz_automation.chatgpt_client import ChatGPTClient


class FailingAPI:
    def __init__(self, *args, **kwargs):
        self.calls = 0

    def create(self, **_: object) -> object:
        self.calls += 1
        if self.calls == 1:
            raise chatgpt_client.OpenAIError("fail")
        return SimpleNamespace(output_text='{"answer":"A"}', usage=SimpleNamespace(total_tokens=1))


class Wrapper:
    def __init__(self, *args, **kwargs):
        self.responses = FailingAPI()


def test_chatgpt_client_retry(monkeypatch):
    monkeypatch.setattr(chatgpt_client, "OpenAI", lambda api_key: Wrapper())
    client = ChatGPTClient("key")
    assert client.ask("Q?") == "A"
