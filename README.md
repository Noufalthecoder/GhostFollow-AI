# GhostFollow AI - Autonomous Customer Follow-Up Agent

GhostFollow AI is a hackathon-ready MVP for the TinyFish Web Agent Hackathon. It identifies ghosted customer conversations, generates intelligent follow-up messages using LLMs, and can deliver them through real Gmail Web automation using Playwright.

## What This MVP Demonstrates

- AI-powered ghosted conversation detection (48h inactivity default)
- Context-aware follow-up generation (OpenAI, Amazon Nova, or fallback template)
- Real browser automation agent that interacts with Gmail Web UI
- Modern startup-style dashboard built with Next.js + TailwindCSS
- AI thinking panel showing autonomous reasoning steps
- Demo mode for reliable live presentations

## Project Structure

```text
ghostfollow-ai/
  frontend/
    components/
    pages/
    dashboard/
    styles/
  backend/
    main.py
    agent.py
    followup_generator.py
    conversation_detector.py
    database.py
    prompts/
    schemas/
  automation/
    gmail_agent.py
  README.md
```

## Tech Stack

- Frontend: Next.js, React, TailwindCSS
- Backend: FastAPI, SQLAlchemy
- DB: PostgreSQL / Supabase compatible schema
- Agent Automation: Playwright (Python)
- LLM: OpenAI or Amazon Nova (Bedrock), with fallback template mode

## Core Features Included

1. Dashboard
- Overview stats cards (total, ghosted, sent, queue)
- Ghosted conversations table
- Follow-up action buttons (generate + send)
- Follow-up status log
- AI reasoning panel
- Agent activity feed

2. Conversation Detection
- `/scan-conversations` checks inactivity threshold (default 48h)
- Marks rows as `ghosted_status=true`

3. AI Follow-Up Generator
- `/generate-followup` creates contextual follow-ups from thread context
- Returns reasoning trace for demo explainability

4. Web Automation Agent
- Playwright Gmail flow:
  - open Gmail
  - search/open thread
  - click reply
  - insert follow-up
  - send message

5. Backend API
- `POST /scan-conversations`
- `POST /generate-followup`
- `POST /send-followup`
- `GET /conversations`
- `GET /followups`
- `GET /activity`

6. Demo Mode
- `DEMO_MODE=true` seeds sample conversations and simulates sends

## Local Setup

## 1) Backend

```bash
cd ghostfollow-ai
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
playwright install chromium
```

Create env file from `backend/.env.example` and set values.

Run API:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 2) Frontend

```bash
cd ghostfollow-ai/frontend
npm install
npm run dev
```

Open: `http://localhost:3000/dashboard`

## 3) Optional PostgreSQL via Docker

```bash
cd ghostfollow-ai
docker compose up -d
```

Use:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ghostfollow
```

## Gmail Automation (Real Web Interaction)

1. Save Gmail auth session once:

```bash
python automation/save_gmail_session.py
```

2. Set env:

```env
DEMO_MODE=false
GMAIL_STORAGE_STATE=storage_state.json
PLAYWRIGHT_HEADLESS=false
```

3. Use `POST /send-followup` from the dashboard or API.

Note: Gmail selectors can change over time. This MVP uses robust selectors and is intended for hackathon demonstration.

## API Payload Examples

### `POST /scan-conversations`

```json
{
  "threshold_hours": 48
}
```

### `POST /generate-followup`

```json
{
  "conversation_id": 1
}
```

### `POST /send-followup`

```json
{
  "conversation_id": 1,
  "dry_run": false
}
```

## Database Schema

SQL schema is provided at:

- `backend/schemas/schema.sql`

Tables:
- `conversations`
- `followups`
- `activity_logs`

## Prompt Assets

- Main prompt: `backend/prompts/followup_prompt.txt`
- Examples: `backend/prompts/example_prompts.md`

## Deployment

## Frontend to Vercel

- Set root to `frontend/`
- Build command: `npm run build`
- Install command: `npm install`
- Env var: `NEXT_PUBLIC_API_BASE=https://<your-backend-url>`

## Backend to Render / Railway

- Use `backend/` as Python service source
- Install dependencies from `backend/requirements.txt`
- Start command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

- Add env vars:
  - `DATABASE_URL`
  - `DEMO_MODE`
  - `OPENAI_API_KEY` (optional)
  - `USE_AMAZON_NOVA`, `AWS_REGION` (optional)
  - `GMAIL_STORAGE_STATE`, `PLAYWRIGHT_HEADLESS`

## Hackathon Demo Script

1. Open dashboard and run Scan Conversations.
2. Show ghosted conversations detected in table.
3. Click AI Follow-up and display AI Thinking Panel steps.
4. Click Send via Gmail.
5. Show activity logs and follow-up success status updates.

## Notes

- This MVP is modular and easy to extend to other channels (LinkedIn, WhatsApp Web, CRM inboxes).
- For production hardening, add OAuth account linking, retries, queueing (Celery/Redis), and strict observability.
