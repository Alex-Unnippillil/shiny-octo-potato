import json
from types import SimpleNamespace

import pytest

from quiz_automation.chatgpt_client import ChatGPTClient


class DummyResponses:
    def create(self, **_: str):  # noqa: D401
        text = json.dumps({"answer": "A"})
        return SimpleNamespace(output=[SimpleNamespace(content=[SimpleNamespace(text=text)])])


class DummyClient:
    responses = DummyResponses()


@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.OpenAI", lambda api_key: DummyClient()
    )
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_api_key", "test-key"
    )


def test_chatgpt_client_parsing():
    client = ChatGPTClient(cache={})
    assert client.ask("question") == "A"


def test_chatgpt_client_malformed_response(monkeypatch):
    class BadResponses:
        def create(self, **_: str):  # noqa: D401
            return SimpleNamespace(
                output=[SimpleNamespace(content=[SimpleNamespace(text="not json")])]
            )

    class BadClient:
        responses = BadResponses()

    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.OpenAI", lambda api_key: BadClient()
    )
    client = ChatGPTClient(cache={})
    assert client.ask("question") == "Error: malformed response"


def test_chatgpt_client_retry(monkeypatch):
    class FlakyResponses:
        def __init__(self):
            self.calls = 0

        def create(self, **_: str):  # noqa: D401
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("boom")
            text = json.dumps({"answer": "A"})
            return SimpleNamespace(
                output=[SimpleNamespace(content=[SimpleNamespace(text=text)])]
            )

    flaky = FlakyResponses()

    class FlakyClient:
        responses = flaky

    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.OpenAI", lambda api_key: FlakyClient()
    )

    sleeps = []

    def fake_sleep(seconds: float) -> None:  # pragma: no cover - helper
        sleeps.append(seconds)

    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.time.sleep", fake_sleep
    )

    client = ChatGPTClient(cache={})
    assert client.ask("question") == "A"
    assert flaky.calls == 2
    assert sleeps == [1.0]


def test_chatgpt_client_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_api_key", ""
    )
    with pytest.raises(ValueError, match="API key is required"):
        ChatGPTClient(cache={})


def test_chatgpt_client_uses_cache(monkeypatch):
    calls = {"count": 0}

    class CountingResponses:
        def create(self, **_: str):  # noqa: D401
            calls["count"] += 1
            text = json.dumps({"answer": "A"})
            return SimpleNamespace(
                output=[SimpleNamespace(content=[SimpleNamespace(text=text)])]
            )

    class CountingClient:
        responses = CountingResponses()

    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.OpenAI", lambda api_key: CountingClient()
    )

    client = ChatGPTClient(cache={})
    question = "What is caching?"
    assert client.ask(question) == "A"
    assert client.ask(question) == "A"
    assert calls["count"] == 1
