from quiz_automation.config import get_settings


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_TEMPERATURE", raising=False)
    monkeypatch.delenv("POLL_INTERVAL", raising=False)
    monkeypatch.delenv("OPENAI_INPUT_COST", raising=False)
    monkeypatch.delenv("OPENAI_OUTPUT_COST", raising=False)
    settings = get_settings()
    assert settings.poll_interval == 0.5
    assert settings.openai_model == "gpt-4o-mini-high"
    assert settings.openai_temperature == 0.0
    assert settings.openai_input_cost == 0.0
    assert settings.openai_output_cost == 0.0


def test_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "abc")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("OPENAI_TEMPERATURE", "0.7")
    monkeypatch.setenv("POLL_INTERVAL", "1.0")
    monkeypatch.setenv("OPENAI_INPUT_COST", "0.5")
    monkeypatch.setenv("OPENAI_OUTPUT_COST", "1.0")
    settings = get_settings()
    assert settings.openai_api_key == "abc"
    assert settings.openai_model == "gpt-4o-mini"
    assert settings.openai_temperature == 0.7
    assert settings.poll_interval == 1.0
    assert settings.openai_input_cost == 0.5
    assert settings.openai_output_cost == 1.0

