# Quiz Automation Starter

This project provides a skeleton for automating multiple‑choice quiz solving
using OCR and the OpenAI API. It includes a Tkinter GUI, background watcher
thread, and SQLite logging.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file at the project root. Supported variables:

| Variable | Default | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | *(required)* | OpenAI API key used for requests. |
| `OPENAI_MODEL` | `gpt-4o-mini-high` | Model passed to the API. |
| `OPENAI_TEMPERATURE` | `0.0` | Sampling temperature for responses. |
| `POLL_INTERVAL` | `0.5` | Seconds between capture polls. |

### OCR requirements

OCR is performed with `pytesseract`, which requires the [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html) binary. Install Tesseract separately and ensure it is on your `PATH`.

## Running

```bash
python run.py
```

### Selecting a capture region

1. Launch the app with `python run.py` and click **Start**.
2. A translucent full‑screen overlay with a crosshair cursor appears.
3. Click and drag to draw a rectangle around the quiz area.
4. Release the mouse button to confirm the selection and begin watching.

## Logs

Quiz events are stored in an SQLite database named `events.db` in the project directory. Inspect it with:

```bash
sqlite3 events.db "SELECT * FROM events;"
```

## Testing

Run linting and tests locally:

```bash
ruff check .
pytest
```

## Further reading

- [OpenAI rate limits](https://platform.openai.com/docs/guides/rate-limits) and [pricing](https://openai.com/pricing)
- [pytesseract documentation](https://pypi.org/project/pytesseract/) and [Tesseract install guide](https://tesseract-ocr.github.io/tessdoc/Installation.html)

## Optimisation Flags

- Adjust `poll_interval` in `config.py` for faster or slower capture.
- Replace placeholder functions with real `mss` capture and OCR logic.
- Extend `chatgpt_client.py` with retry and cost tracking.
