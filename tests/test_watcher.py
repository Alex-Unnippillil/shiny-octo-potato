from threading import Event
from PIL import Image

from quiz_automation.watcher import Watcher


def test_is_new_question() -> None:
    def on_question(_: str) -> None:
        pass

    watcher = Watcher((0, 0, 1, 1), on_question)
    assert watcher.is_new_question("q1")
    watcher._last_text = "q1"  # simulate previous question
    assert not watcher.is_new_question("q1")


def test_run_calls_on_question_and_saves(tmp_path, mocker) -> None:
    texts = ["q1"]

    def capture(_: tuple[int, int, int, int]) -> Image.Image:
        return Image.new("RGB", (1, 1))

    def ocr(_: Image.Image) -> str:
        if texts:
            return texts.pop(0)
        watcher.stop_flag.set()
        return ""

    ocr_mock = mocker.Mock(side_effect=ocr)
    on_question = mocker.Mock()
    mocker.patch("time.time", return_value=1234)

    watcher = Watcher(
        (0, 0, 1, 1),
        on_question,
        poll_interval=0.01,
        screenshot_dir=tmp_path,
        capture=capture,
        ocr=ocr_mock,
    )

    watcher.start()
    watcher.join(timeout=1)

    assert not watcher.is_alive()
    on_question.assert_called_once_with("q1")
    assert (tmp_path / "1234.png").exists()


def test_run_survives_capture_and_ocr_errors(mocker) -> None:
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
