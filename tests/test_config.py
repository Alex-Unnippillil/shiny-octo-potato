from quiz_automation.config import settings


def test_config_defaults():
    assert settings.poll_interval == 0.5
    assert settings.openai_model == "gpt-4o-mini-high"
    assert settings.openai_temperature == 0.0
