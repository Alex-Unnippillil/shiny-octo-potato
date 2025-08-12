import json
from types import SimpleNamespace

import pytest

from quiz_automation.chatgpt_client import ChatGPTClient
from quiz_automation.config import get_settings


class DummyResponses:
    def create(self, **_: str):  # noqa: D401
        text = json.dumps({"answer": "A"})
        return SimpleNamespace(output=[SimpleNamespace(content=[SimpleNamespace(text=text)])])


class DummyClient:
    responses = DummyResponses()


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    get_settings.cache_clear()
    monkeypatch.setattr("quiz_automation.chatgpt_client.OpenAI", lambda api_key: DummyClient())


def test_chatgpt_client_parsing():
    client = ChatGPTClient()
    assert client.ask("question") == "A"
