# Quiz Automation Starter

This project provides a foundation for automating multiple-choice quizzes using
screen capture, OCR, and the OpenAI API.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Create a `.env` file** with your OpenAI API key:
   ```env
   OPENAI_API_KEY="sk-your-key"
   ```
3. **Run the GUI**
   ```bash
   python run.py
   ```

## Testing

Run unit tests with:
```bash
pytest
```

## Optimisation Flags

Environment variables control behaviour:

- `POLL_INTERVAL` – seconds between screen captures (default 0.5)
- `OPENAI_API_KEY` – key for ChatGPT access

## Project Layout

- `quiz_automation/` – package containing core modules
- `tests/` – unit tests with mocks
- `run.py` – application entry point
