# Quiz Automation Starter

This project automates multiple-choice quizzes by capturing a screen region,
performing OCR, querying ChatGPT for the answer, and clicking the matching
option. Actions are persisted to SQLite for later review.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Create a `.env` file** with your OpenAI API key:
   ```env
   OPENAI_API_KEY="sk-your-key"
   ```

## Usage

Run the GUI entry point:
```bash
python run.py
```
On first start the application prompts you to mark the quiz area:
1. Move the mouse to the **top-left** of the question box and press Enter.
2. Move to the **bottom-right** corner and press Enter.
3. Finally, move to the **centre of answer A** and press Enter.

The selection is stored in `region.json` and reused on subsequent runs. The GUI
then watches the region, asks ChatGPT for each new question and clicks the
returned option.

## Testing

```bash
ruff check .
pytest -q
```

## Environment Variables

- `POLL_INTERVAL` – seconds between screen captures (default 0.5)
- `OPENAI_API_KEY` – key for ChatGPT access
- `DB_PATH` – SQLite database location (default `quiz_log.sqlite`)

## Project Layout

- `quiz_automation/` – core modules
- `tests/` – unit tests with mocks
- `run.py` – application entry point
