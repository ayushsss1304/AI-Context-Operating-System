# AI Context Operating System

A shared memory and workflow-continuity layer for AI-native teams using multiple AI agents, copilots, and automation tools.

## Current Status

This repo has the first backend skeleton for the MVP:

- FastAPI app
- SQLModel data models
- CRUD APIs for workspaces, agents, memories, tasks, activities, and approvals
- Demo customer-issue workflow
- Docker Compose PostgreSQL with pgvector enabled

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

Open:

```txt
http://127.0.0.1:8000/docs
```

## Demo Flow

1. Create a workspace with `POST /workspaces`.
2. Run `POST /workflows/customer-issue-demo` using the workspace ID.
3. Inspect created memories with `GET /memories?workspace_id=...`.
4. Inspect task activity with `GET /activities?workspace_id=...`.
5. Approve or reject the pending approval.

## Next Build Step

Replace the deterministic demo workflow summaries with LangGraph-powered agent steps while keeping every memory write, memory retrieval, and approval request logged in the activity timeline.
