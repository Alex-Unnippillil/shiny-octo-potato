from unittest.mock import patch

import pytest
import pyautogui  # noqa: F401  # ensure stub is loaded

from quiz_automation.clicker import click_answer


def test_click_answer_coordinates():
    region = (0, 0, 100, 400)
    with patch("quiz_automation.clicker.pyautogui.click") as mock_click:
        x, y = click_answer("C", region)
        mock_click.assert_called_once_with(x, y)
        assert (x, y) == (50, 250)


def test_click_answer_invalid_letter():
    region = (0, 0, 100, 400)
    with patch("quiz_automation.clicker.pyautogui.click") as mock_click:
        with pytest.raises(ValueError):
            click_answer("E", region)
        mock_click.assert_not_called()


def test_click_answer_custom_option_count():
    region = (0, 0, 100, 500)
    with patch("quiz_automation.clicker.pyautogui.click") as mock_click:
        x, y = click_answer("E", region, num_options=5)
        mock_click.assert_called_once_with(x, y)
        assert (x, y) == (50, 450)
