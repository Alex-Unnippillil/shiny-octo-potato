from quiz_automation.watcher import Watcher


def test_is_new_question():
    def on_question(text: str) -> None:
        pass

    watcher = Watcher((0, 0, 1, 1), on_question)
    assert watcher.is_new_question("q1")
    watcher._last_text = "q1"
    assert not watcher.is_new_question("q1")
