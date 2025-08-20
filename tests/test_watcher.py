from threading import Event
from PIL import Image

from quiz_automation.watcher import Watcher
from quiz_automation.utils import hash_text


def test_watcher_initialization():
    """Watcher stores provided region and callbacks."""

    region = (0, 0, 1, 1)
    w = Watcher(region, lambda _: None, capture=lambda r: None, ocr=lambda i: "")
    assert w.region == region


def test_is_new_question() -> None:
    def on_question(_: str) -> None:
        pass

    watcher = Watcher((0, 0, 1, 1), on_question)
    assert watcher.is_new_question("q1")
    watcher._last_text = "q1"  # simulate previous question
    assert not watcher.is_new_question("q1")


def test_run_calls_on_question_and_saves_once(tmp_path, mocker) -> None:
    texts = ["q1", "q1"]

    def capture(_: tuple[int, int, int, int]) -> Image.Image:
        return Image.new("RGB", (1, 1))

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
        screenshot_dir=tmp_path,
        capture=capture,
        ocr=ocr_mock,
    )

    watcher.start()
    watcher.join(timeout=1)

    assert not watcher.is_alive()
    on_question.assert_called_once_with("q1")
    files = list(tmp_path.iterdir())
    assert files == [tmp_path / f"{hash_text('q1')}.png"]


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
