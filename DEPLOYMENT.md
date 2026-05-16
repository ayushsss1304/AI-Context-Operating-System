# Deployment Notes

The MVP can be deployed as a single FastAPI app with the Python dashboard enabled.

## Recommended MVP Deployment

- App host: Render, Railway, Fly.io, or similar Python web service
- Database: managed PostgreSQL
- Frontend: use the FastAPI dashboard first; the Next.js app is optional

This repo includes `render.yaml` for Render Blueprint deployment.

## Required Environment Variables

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/database
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=your_key_here
AUTO_CREATE_TABLES=false
APP_ENV=production
```

Optional providers:

```env
OPENROUTER_API_KEY=your_key_here
TOGETHER_API_KEY=your_key_here
```

## Build Command

```bash
cd backend
pip install -r requirements.txt
```

## Migration Command

```bash
cd backend
python -m alembic upgrade head
```

## Start Command

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

On Windows local development, use:

```bash
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Post-Deploy Smoke Test

Open:

```txt
https://your-app-url/health
https://your-app-url/dashboard
https://your-app-url/system/status
```

Then create a demo:

```txt
POST /workflows/demo-bootstrap
```

Expected result:

- 4 registered agents
- 1 task
- 3 memories
- 1 pending approval
- 5 handoff events
- `/system/status` reports `ready`

## Production Notes

- Keep `AUTO_CREATE_TABLES=false` in hosted environments.
- Run Alembic migrations during deploy.
- Do not commit `.env` files.
- Use managed PostgreSQL backups.
- Keep the Python dashboard as the MVP UI until a separate frontend is required.

## Render Blueprint Steps

1. Push the repo to GitHub.
2. In Render, create a new Blueprint from the GitHub repo.
3. Render will read `render.yaml`.
4. Set `GROQ_API_KEY` in the web service environment.
5. Deploy.
6. Open `/health`, `/dashboard`, and `/system/status`.
7. Run `POST /workflows/demo-bootstrap` once to seed a demo workspace.
