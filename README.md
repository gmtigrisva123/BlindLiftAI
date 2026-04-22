# BlindLiftAI

BlindLiftAI is a voice-first backend for accessible math practice, microbusiness tracking, and daily task support for visually impaired learners.

## What is included

- `VoiceMath`: creates spoken-friendly arithmetic exercises and checks answers.
- `VoiceCommerce`: manages products, sales, stock, and revenue summaries.
- `VoiceAssistant`: stores reminders and generates a simple daily brief.
- FastAPI service with SQLite persistence in `data/blindlift_ai.db`.

## Project structure

- `src/blindlift_ai`: application package
- `test`: service and API tests
- `docs`: product notes and future architecture research
- `data`: runtime SQLite database

## Quick start

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Run the API:

```bash
$env:PYTHONPATH="src"
python -m uvicorn blindlift_ai.main:app --reload
```

3. Open the docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Example endpoints

- `POST /math/exercises`
- `POST /math/exercises/{exercise_id}/answer`
- `POST /commerce/products`
- `POST /commerce/sales`
- `GET /commerce/summary`
- `POST /assistant/reminders`
- `GET /assistant/daily-brief`

## Testing

```bash
python -m pytest
```

## Next steps

- Replace the placeholder voice adapter with Whisper and TTS integrations.
- Add authentication and per-student profiles.
- Expand math content beyond arithmetic into guided multi-step lessons.
- Add a frontend or mobile client for real voice interaction.
