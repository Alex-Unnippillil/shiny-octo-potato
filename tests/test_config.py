from __future__ import annotations

from quiz_automation.config import get_settings


def test_config_loads_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    cfg = get_settings()
    assert cfg.openai_api_key == "secret"
