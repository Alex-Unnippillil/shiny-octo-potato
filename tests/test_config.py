from quiz_automation.config import get_settings


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("POLL_INTERVAL", "1.5")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.openai_api_key == "test-key"
    assert settings.poll_interval == 1.5

