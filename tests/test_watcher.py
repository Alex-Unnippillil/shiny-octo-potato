from quiz_automation.watcher import Watcher


def test_watcher_initialization():
    """Watcher stores provided region and callbacks."""

    region = (0, 0, 1, 1)
    w = Watcher(region, lambda _: None, capture=lambda r: None, ocr=lambda i: "")
    assert w.region == region
