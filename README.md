# LinkedIn AI Content Agent

Production-ready MVP backend for generating, managing, scheduling, and distributing LinkedIn content for a personal brand and a cigar brand.

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- APScheduler
- OpenAI Responses API
- SMTP, SendGrid, or Resend for email

## Features

- Generate 3-5 LinkedIn posts from a raw idea
- Save posts to PostgreSQL
- Schedule posts by date and time
- Auto-process scheduled posts with a mock LinkedIn publisher
- Generate suggested replies and 5 daily engagement comments
- Send weekly cigar brand and personal brand email digests
- Deploy cleanly to Render

## Project Structure

```text
app/
  api/
  core/
  db/
  models/
  schemas/
  services/
```

## Environment Variables

Copy `.env.example` to `.env` and fill in the values.

Required:

- `OPENAI_API_KEY`
- `DATABASE_URL`
- `EMAIL_FROM`
- `WEEKLY_REPORT_EMAIL`

Common:

- `OPENAI_MODEL`
- `EMAIL_PROVIDER`
- `EMAIL_PROVIDER_API_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`
- `LINKEDIN_MOCK_MODE`
- `APP_TIMEZONE`

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

App runs on `http://127.0.0.1:8000`.

## API Endpoints

- `POST /generate-posts`
- `POST /save-post`
- `POST /schedule-post`
- `GET /get-posts`
- `POST /generate-comments`
- `POST /send-weekly-cigar-email`
- `POST /send-weekly-personal-email`
- `GET /health`

## Example Requests

Generate posts:

```bash
curl -X POST http://127.0.0.1:8000/generate-posts \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Why most product teams misuse AI features",
    "topic": "AI in Product & Technology",
    "brand": "personal",
    "count": 3
  }'
```

Save a post:

```bash
curl -X POST http://127.0.0.1:8000/save-post \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Most AI roadmaps are theater until they solve a real workflow.\n\nThe shiny demo is easy.\nThe habit change is hard.\n\nWhat workflow are you actually improving?",
    "topic": "AI in Product & Technology",
    "status": "DRAFT"
  }'
```

Schedule a post:

```bash
curl -X POST http://127.0.0.1:8000/schedule-post \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": 1,
    "scheduled_at": "2026-04-12T09:00:00-04:00"
  }'
```

Generate engagement content:

```bash
curl -X POST http://127.0.0.1:8000/generate-comments \
  -H "Content-Type: application/json" \
  -d '{
    "post_content": "Shipping fast matters, but clarity matters more.",
    "incoming_comments": [
      "This is why product leaders need stronger prioritization.",
      "Could not agree more."
    ]
  }'
```

Send weekly cigar email:

```bash
curl -X POST http://127.0.0.1:8000/send-weekly-cigar-email \
  -H "Content-Type: application/json" \
  -d '{}'
```

Send weekly personal email:

```bash
curl -X POST http://127.0.0.1:8000/send-weekly-personal-email \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Weekly Email Schedule

The app starts a scheduler on boot and automatically runs:

- Weekly cigar digest: Sunday at 7:00 PM America/New_York
- Weekly personal digest: Sunday at 7:00 PM America/New_York
- Scheduled post processor: every 5 minutes

## Render Deployment

1. Create a new Render Blueprint and point it to this repository.
2. Render will read `render.yaml` and provision:
   - One Python web service
   - One PostgreSQL database
3. Set the secret environment variables in Render:
   - `OPENAI_API_KEY`
   - `EMAIL_PROVIDER_API_KEY` if using Resend or SendGrid
   - `EMAIL_FROM`
   - `WEEKLY_REPORT_EMAIL`
   - SMTP credentials if using SMTP
4. Deploy.

## Notes

- The LinkedIn publishing layer is intentionally mocked by default so the scheduler can run safely without a live LinkedIn API app.
- Keep the Render service at a single web instance if you want to avoid duplicate in-app cron execution.
- Tables are created automatically on startup for the MVP.
