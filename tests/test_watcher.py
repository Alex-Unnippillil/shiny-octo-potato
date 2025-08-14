"""Tests for the :mod:`quiz_automation.watcher` module."""

from __future__ import annotations

from threading import Event



def test_is_new_question() -> None:
    """``is_new_question`` returns ``True`` only for unseen text."""

    def on_question(_: str) -> None:  # pragma: no cover - helper callback
        pass

    watcher = Watcher((0, 0, 1, 1), on_question)
    assert watcher.is_new_question("q1")
    watcher._last_text = "q1"  # simulate previous question
    assert not watcher.is_new_question("q1")


def test_run_triggers_on_question(mocker) -> None:
    """Watcher calls ``on_question`` when OCR detects new text."""

    capture = mocker.Mock(return_value=Image.new("RGB", (1, 1)))
    texts = ["q1", "q1"]  # second value keeps thread alive once more

    def ocr(_: Image.Image) -> str:
        if texts:
            return texts.pop(0)
        watcher.stop_flag.set()
        return ""

    ocr_mock = mocker.Mock(side_effect=ocr)
    on_question = mocker.Mock()

    watcher = Watcher(
        (0, 0, 1, 1),
        on_question,
        poll_interval=0.01,
        capture=capture,
        ocr=ocr_mock,
    )

    watcher.start()
    watcher.join(timeout=1)

    assert not watcher.is_alive()
    on_question.assert_called_once_with("q1")


def test_run_survives_capture_and_ocr_errors(mocker) -> None:
    """Errors from capture or OCR are reported but do not stop the thread."""

    capture_event = Event()
    ocr_event = Event()
    errors: list[Exception] = []

    def capture(_: tuple[int, int, int, int]) -> Image.Image:
        if not capture_event.is_set():
            capture_event.set()
            raise RuntimeError("capture fail")
        return Image.new("RGB", (1, 1))

    def ocr(_: Image.Image) -> str:
        if not ocr_event.is_set():
            ocr_event.set()
            raise RuntimeError("ocr fail")
        watcher.stop_flag.set()
        return "q1"

    on_question = mocker.Mock()

    watcher = Watcher(
        (0, 0, 1, 1),
        on_question,
        poll_interval=0.01,
        capture=capture,
        ocr=ocr,
        on_error=errors.append,
    )

    watcher.start()

    assert capture_event.wait(0.5)
    assert watcher.is_alive()

    assert ocr_event.wait(0.5)
    assert watcher.is_alive()

    watcher.join(timeout=1)
    assert not watcher.is_alive()

    on_question.assert_called_once_with("q1")
    assert len(errors) == 2


