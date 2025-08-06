from unittest.mock import patch

from quiz_automation.clicker import click_answer


def test_click_answer_coordinates():
    region = (0, 0, 100, 400)
    with patch("quiz_automation.clicker.pyautogui.click") as mock_click:
        x, y = click_answer("C", region)
        mock_click.assert_called_once_with(x, y)
        assert (x, y) == (50, 250)
