from threading import Event
from PIL import Image

from PIL import Image
from quiz_automation.watcher import Watcher


def test_is_new_question():
    def on_question(text: str) -> None:
        pass

    watcher = Watcher((0, 0, 1, 1), on_question)
    assert watcher.is_new_question("q1")
    watcher._last_text = "q1"
    assert not watcher.is_new_question("q1")


def test_run_triggers_on_question(mocker):
    capture = mocker.Mock(return_value=None)
    texts = ["q1", "q1"]

    def ocr(_):
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


def test_run_survives_capture_and_ocr_errors(mocker):
    capture_event = Event()
    ocr_event = Event()
    errors: list[Exception] = []

    def capture(_):
        if not capture_event.is_set():
            capture_event.set()
            raise RuntimeError("capture fail")
        return None

    def ocr(_):
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




    watcher = Watcher(
        (0, 0, 1, 1),
        on_question,
        poll_interval=0.01,

    watcher.start()
    watcher.join(timeout=1)
    assert not watcher.is_alive()
    on_question.assert_called_once_with("q1")

