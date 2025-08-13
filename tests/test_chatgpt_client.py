import json
from types import SimpleNamespace

import pytest

from quiz_automation.chatgpt_client import ChatGPTClient


class DummyResponses:
    def create(self, **_: str):  # noqa: D401
        text = json.dumps({"answer": "A"})
        return SimpleNamespace(
            output=[SimpleNamespace(content=[SimpleNamespace(text=text)])],
            usage=SimpleNamespace(input_tokens=1000, output_tokens=2000),
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
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_input_cost", 0.1
    )
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_output_cost", 0.2
    )


def test_chatgpt_client_parsing():
    client = ChatGPTClient()
    answer, usage, cost = client.ask("question")
    assert answer == "A"
    assert usage.input_tokens == 1000
    assert usage.output_tokens == 2000
    assert cost == pytest.approx(0.5)


def test_chatgpt_client_malformed_response(monkeypatch):
    class BadResponses:
        def create(self, **_: str):  # noqa: D401
            return SimpleNamespace(
                output=[SimpleNamespace(content=[SimpleNamespace(text="not json")])],
                usage=SimpleNamespace(input_tokens=10, output_tokens=20),
            )

    class BadClient:
        responses = BadResponses()

    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.OpenAI", lambda api_key: BadClient()
    )
    client = ChatGPTClient()
    answer, usage, cost = client.ask("question")
    assert answer == "Error: malformed response"
    assert usage.input_tokens == 10
    assert usage.output_tokens == 20
    assert cost == pytest.approx(10 / 1000 * 0.1 + 20 / 1000 * 0.2)


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
                usage=SimpleNamespace(input_tokens=1000, output_tokens=2000),
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
    assert usage.input_tokens == 1000
    assert cost == pytest.approx(0.5)
    assert flaky.calls == 2
    assert sleeps == [1.0]


def test_chatgpt_client_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        "quiz_automation.chatgpt_client.settings.openai_api_key", ""
    )
    with pytest.raises(ValueError, match="API key is required"):
        ChatGPTClient()
