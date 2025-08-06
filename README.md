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

Create a `.env` file with your OpenAI key:

```
OPENAI_API_KEY=sk-...
```

## Running

```bash
python run.py
```

## Testing

```bash
ruff check .
pytest
```

## Optimisation Flags

- Adjust `poll_interval` in `config.py` for faster or slower capture.
- Replace placeholder functions with real `mss` capture and OCR logic.
- Extend `chatgpt_client.py` with retry and cost tracking.
