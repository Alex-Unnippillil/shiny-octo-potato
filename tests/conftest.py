"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

BASE_DIR = Path(__file__).resolve().parent
# Ensure the project root is importable
sys.path.insert(0, str(BASE_DIR.parent))


@pytest.fixture
def noop_openai_and_click(monkeypatch):
    """Patch OpenAI responses and ``pyautogui.click`` to no-op."""

    class DummyResponses:
        def create(self, **_: str):  # pragma: no cover - stub helper
            return SimpleNamespace(output=[], usage=None)

    client = SimpleNamespace(responses=DummyResponses())

    monkeypatch.setattr("openai.OpenAI", lambda *_, **__: client)
    monkeypatch.setattr("pyautogui.click", lambda *_, **__: None)

    return client

