import json
from types import SimpleNamespace

import pytest

from quiz_automation.chatgpt_client import ChatGPTClient


class DummyResponses:
    def create(self, **_: str):  # noqa: D401
        text = json.dumps({"answer": "A"})
        return SimpleNamespace(
            output=[SimpleNamespace(content=[SimpleNamespace(text=text)])],
            usage=SimpleNamespace(input_tokens=10, output_tokens=20),
        )


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
    monkeypatch.setattr("quiz_automation.chatgpt_client.CACHE", {})


def test_chatgpt_client_parsing(monkeypatch):
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_input_cost", 1.0
    )
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_output_cost", 2.0
    )
    client = ChatGPTClient()
    answer, usage, cost = client.ask("question")
    assert answer == "A"
    assert usage.input_tokens == 10
    assert usage.output_tokens == 20
    assert cost == (10 * 1.0 + 20 * 2.0) / 1000


def test_chatgpt_client_malformed_response(monkeypatch):
    class BadResponses:
        def create(self, **_: str):  # noqa: D401
            return SimpleNamespace(
                output=[SimpleNamespace(content=[SimpleNamespace(text="not json")])],
                usage=SimpleNamespace(input_tokens=0, output_tokens=0),
            )

    class BadClient:
        responses = BadResponses()

    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.OpenAI", lambda api_key: BadClient()
    )
    client = ChatGPTClient()
    answer, usage, cost = client.ask("question")
    assert answer == "Error: malformed response"
    assert usage is None
    assert cost == 0.0


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
                output=[SimpleNamespace(content=[SimpleNamespace(text=text)])],
                usage=SimpleNamespace(input_tokens=0, output_tokens=0),
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

    client = ChatGPTClient()
    answer, usage, cost = client.ask("question")
    assert answer == "A"
    assert cost == 0.0
    assert flaky.calls == 2
    assert sleeps == [1.0]


def test_chatgpt_client_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_api_key", "",
    )
    with pytest.raises(ValueError, match="API key is required"):
        ChatGPTClient()


def test_chatgpt_client_uses_cache(monkeypatch):
    class CountingResponses:
        def __init__(self):
            self.calls = 0

        def create(self, **_: str):  # noqa: D401
            self.calls += 1
            text = json.dumps({"answer": "A"})
            return SimpleNamespace(
                output=[SimpleNamespace(content=[SimpleNamespace(text=text)])]
            )

    counting = CountingResponses()

    class CountingClient:
        responses = counting

    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.OpenAI", lambda api_key: CountingClient()
    )

    client = ChatGPTClient()
    answer1, _, _ = client.ask("question")
    answer2, usage2, cost2 = client.ask("question")
    assert answer1 == answer2 == "A"
    assert usage2 is None
    assert cost2 == 0.0
    assert counting.calls == 1

