# AI Context Operating System

A shared memory and workflow-continuity layer for AI-native teams using multiple AI agents, copilots, and automation tools.

## Current Status

This repo contains the working MVP:

- FastAPI app
- SQLModel data models
- CRUD APIs for workspaces, agents, memories, tasks, activities, and approvals
- LangGraph-powered demo customer-issue workflow
- Python-rendered dashboard with workspace, agent registry, shared memory, timeline, and approval views
- Docker Compose PostgreSQL with pgvector enabled
- Context packets for workflow continuation
- One-call demo bootstrap
- System readiness endpoint

## Local Setup

Start PostgreSQL:

```bash
docker compose up -d
```

If Docker Desktop is not running yet, you can still smoke-test the API with SQLite:

```bash
cd backend
$env:DATABASE_URL="sqlite:///./dev.db"
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Create a Python virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the API:

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Run backend tests:

```bash
.venv\Scripts\python.exe -m pytest
```

Run database migrations:

```bash
cd backend
.venv\Scripts\python.exe -m alembic upgrade head
```

Create a new migration after model changes:

```bash
cd backend
.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe change"
```

For early local development, `AUTO_CREATE_TABLES=true` keeps the app forgiving by creating missing tables on startup. For production-like environments, set `AUTO_CREATE_TABLES=false` and rely on Alembic migrations.

Open the Python-rendered dashboard:

```txt
http://127.0.0.1:8000/dashboard
```

Or open the interactive API docs:

```txt
http://127.0.0.1:8000/docs
```

For a guided demo, see [DEMO.md](DEMO.md).

For deployment notes, see [DEPLOYMENT.md](DEPLOYMENT.md).

For MVP release notes, see [RELEASE_NOTES.md](RELEASE_NOTES.md).

## Demo Flow

1. Create a workspace with `POST /workspaces`.
2. The demo workspace registers Support, Engineering, Product, and Manager agents.
3. Run `POST /workflows/customer-issue-demo` using the workspace ID.
4. Inspect created memories with `GET /memories?workspace_id=...`.
5. Inspect task activity with `GET /activities?workspace_id=...`.
6. Approve or reject the pending approval.

For a one-call demo setup, use `POST /workflows/demo-bootstrap`. It creates a workspace, runs the customer issue workflow, and returns the workflow result plus workspace overview.

## MVP Status

The core MVP is complete. Remaining work should focus on deployment, fresh-environment verification, and production hardening.

## Current Architecture

The main MVP path is Python-first:

- FastAPI serves the API and dashboard.
- PostgreSQL stores workspace, agent, memory, task, activity, and approval records.
- Alembic owns database schema migrations.
- LangGraph orchestrates the customer issue workflow.
- The Support, Engineering, and Product graph nodes call the configured LLM provider.
- Memories receive local vector embeddings when they are created.
- Memory search ranks results by vector similarity with keyword fallback.
- Jinja2 renders the `/dashboard` page.
- The dashboard shows workspace, agent registry, task list, task detail, handoff timeline, memory search, and approvals.
- The handoff timeline renders each workflow event in chronological order with the actor, incoming context, and output.
- Workflow API responses include the same `handoff_trace` used by the dashboard, so external clients can show the continuity chain without rebuilding it.
- Approval and rejection actions update the task status, store a manager review note, and write an audit event to the activity timeline.

The current graph sequence is:

```txt
create_task
  -> support_agent
     stores customer issue as shared memory
  -> engineering_agent
     searches shared memory for relevant context
  -> product_agent
  -> manager_agent
  -> approval request
```

## LLM Configuration

Set keys in `backend/.env`:

```env
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=your_groq_api_key_here
```

Supported provider values:

- `groq`
- `openrouter`
- `together`

If an LLM call fails, the workflow still completes with deterministic fallback text.

Agent outputs are cleaned before storage so the dashboard stays readable. The workflow asks agents for concise plain text and strips common markdown formatting from provider responses.

## Memory Search

Every new memory is embedded on write using a lightweight local feature-hashing embedding. This keeps local development simple while preserving the same product behavior:

```txt
memory text -> embedding vector -> similarity-ranked retrieval
```

Use memory search from:

- `/dashboard`, using the Search Memories field
- `POST /memories/search`

The Docker setup enables the PostgreSQL `vector` extension for future pgvector migration. The current local implementation stores vectors in JSON so it also works with a manually installed PostgreSQL database that may not have pgvector installed.

## Workspace Overview API

Use `GET /workspaces/{workspace_id}/overview` to fetch the current operating-system state in one call:

- workspace details
- registered agents
- tasks
- shared memories
- approvals
- active task
- active task handoff trace

## System Status API

Use `GET /system/status` to check MVP readiness. It returns module-level readiness, record counts, LLM provider configuration status, and whether demo data exists for the core shared-memory workflow.

## Task Context Packet API

Use `GET /tasks/{task_id}/context-packet` when an agent or human needs to resume work on a task. It returns:

- task details
- current owner
- relevant shared memories
- approvals
- handoff trace
- resume summary

Use `POST /tasks/{task_id}/continue` to let an agent resume from the context packet. The endpoint writes a continuation memory, updates task ownership, and records a `task_continued` handoff event.

## Optional JavaScript Frontend

The main app can now be used from the Python FastAPI dashboard at `/dashboard`.
The Next.js frontend is optional if you want a separate JavaScript UI later.

Run the optional JS dashboard:

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

Open:

```txt
http://localhost:3000
```
