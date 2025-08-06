from quiz_automation.config import settings


def test_config_defaults():
    assert settings.poll_interval == 0.5
