from unittest.mock import MagicMock, patch

from quiz_automation.region_selector import Region, select_region


def test_region_as_tuple():
    r = Region(1, 2, 3, 4)
    assert r.as_tuple() == (1, 2, 3, 4)


def test_select_region_user_drag():
    """Simulate a user dragging a box and ensure coordinates are returned."""
    callbacks = {}

    mock_root = MagicMock()
    mock_canvas = MagicMock()

    def bind(event, func):
        callbacks[event] = func

    mock_canvas.bind.side_effect = bind

    def fake_mainloop():
        callbacks["<ButtonPress-1>"](MagicMock())
        callbacks["<ButtonRelease-1>"](MagicMock())

    mock_root.mainloop.side_effect = fake_mainloop

    with patch("quiz_automation.region_selector.tk.Tk", return_value=mock_root), \
        patch("quiz_automation.region_selector.tk.Canvas", return_value=mock_canvas), \
        patch(
            "quiz_automation.region_selector.pyautogui.position",
            side_effect=[(10, 20), (110, 120)],
            create=True,
        ), \
        patch(
            "quiz_automation.region_selector.pyautogui.size",
            return_value=(200, 200),
            create=True,
        ):
        region = select_region()

    assert region.as_tuple() == (10, 20, 100, 100)
