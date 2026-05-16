# AI Context Operating System - Project Plan

## Repository

Target GitHub repository:

```txt
ayushsss1304/AI-Context-Operating-System
```

Visibility:

```txt
public
```

If using GitHub manually, create a public repository named `AI-Context-Operating-System`.

## Product Goal

Build a demo-friendly MVP that proves multiple AI agents can share memory, continue workflows across sessions, and give humans visibility and approval control.

The product is not a chatbot. It is an operating layer for shared organizational context, agent handoff, activity history, and human oversight.

## MVP Demo Flow

1. A user submits a customer issue.
2. Support Agent summarizes the issue and stores it as shared memory.
3. Engineering Agent retrieves relevant memories and creates a technical investigation note.
4. Product Agent reads the support and engineering context and creates a product impact summary.
5. Manager Agent requests human approval for the final recommendation.
6. A human reviews the full activity timeline and approves or rejects the recommendation.

## Phase 1 - Repository And Foundation

Status: complete.

Deliverables:

- Monorepo structure.
- `AGENTS.md` project brief.
- `README.md` with local setup instructions.
- `.env.example` with placeholder environment variables.
- `docker-compose.yml` for PostgreSQL with pgvector.
- Backend and frontend folders created, with backend prioritized.

Suggested structure:

```txt
ai-context-os/
  AGENTS.md
  PLAN.md
  README.md
  docker-compose.yml
  .env.example
  backend/
  frontend/
```

## Phase 2 - Backend Data Model

Status: complete.

Build the FastAPI backend first.

Core entities:

- Workspace
- Agent
- Memory
- Task
- Activity
- Approval

Backend deliverables:

- FastAPI app skeleton.
- Config module using environment variables.
- Database connection module.
- SQLAlchemy or SQLModel models.
- Pydantic request and response schemas.
- Alembic migrations if the migration setup is lightweight.
- Health endpoint.

Acceptance criteria:

- The API starts locally.
- PostgreSQL connects successfully.
- Tables can be created through migrations or startup setup.
- Seed data can create the default demo agents.

## Phase 3 - CRUD APIs

Status: complete.

Implement REST endpoints before agent orchestration.

Endpoints:

```txt
GET    /health

POST   /workspaces
GET    /workspaces
GET    /workspaces/{workspace_id}

POST   /agents
GET    /agents?workspace_id=
GET    /agents/{agent_id}

POST   /memories
GET    /memories?workspace_id=
GET    /memories/{memory_id}
POST   /memories/search

POST   /tasks
GET    /tasks?workspace_id=
GET    /tasks/{task_id}
PATCH  /tasks/{task_id}

GET    /activities?workspace_id=&task_id=

POST   /approvals
GET    /approvals?workspace_id=&status=
POST   /approvals/{approval_id}/approve
POST   /approvals/{approval_id}/reject
```

Acceptance criteria:

- A workspace can be created.
- Demo agents can be listed.
- Memories can be created and searched.
- Tasks can track status changes.
- Every important action can be logged to the activity timeline.
- Approvals can be approved or rejected.

## Phase 4 - Shared Memory Search

Status: complete for MVP.

Start simple, then improve.

Initial implementation:

- Store memory title, content, type, tags, source, and importance score.
- Add an embedding column using pgvector.
- Add a memory search endpoint.
- If embeddings are not configured yet, support a fallback keyword search for local development.

Acceptance criteria:

- One agent can store a memory.
- Another agent can retrieve relevant memory later.
- Search results include enough metadata to explain why the memory matters.

## Phase 5 - Agent Workflow

Status: complete for MVP.

Use LangGraph as the workflow engine, not as the whole product.

Workflow:

```txt
Support Agent
  -> Store customer issue memory
  -> Engineering Agent retrieves memory
  -> Engineering Agent creates technical note
  -> Product Agent creates product impact summary
  -> Manager Agent creates approval request
```

Endpoint:

```txt
POST /workflows/customer-issue-demo
```

Acceptance criteria:

- The endpoint accepts a customer issue.
- A task is created.
- Each agent step creates an activity record.
- Memories are created and retrieved during the workflow.
- A pending approval is created at the end.

## Phase 6 - Frontend Dashboard

Status: complete for MVP using the Python FastAPI dashboard.

Build the frontend after the backend flow works.

Pages:

- Dashboard: summary cards, recent activity, pending approvals.
- Agents: role and capability list.
- Memories: searchable memory list and detail view.
- Tasks: task status and linked timeline.
- Approvals: approve or reject pending outputs.

Design direction:

- Clean, operational, and demo-friendly.
- Prioritize clarity and auditability.
- Avoid marketing-page layout.
- Show the activity timeline as the core product surface.

Acceptance criteria:

- A user can submit the demo customer issue.
- The dashboard shows agent activity as the workflow runs.
- Memories and task details are inspectable.
- A human can approve or reject the final recommendation.

## Phase 7 - Demo Polish

Status: complete for MVP.

Add only what helps the MVP story.

Demo polish:

- Seed workspace and demo agents.
- One-click sample customer issue.
- Clear status labels.
- Human-readable activity summaries.
- Useful empty states.
- README demo script.

Avoid in V1:

- Enterprise SSO.
- Billing.
- Complex RBAC.
- External integrations.
- Agent marketplace.
- Kubernetes.
- Fine-tuning.
- Mobile app.

## First Implementation Order

1. Create monorepo files.
2. Build FastAPI backend skeleton.
3. Add PostgreSQL and pgvector Docker Compose.
4. Implement database models.
5. Add CRUD endpoints.
6. Add memory search.
7. Add LangGraph demo workflow.
8. Add frontend dashboard.
9. Polish the demo flow.

## MVP Success Criteria

The MVP is successful when a user can:

1. Create or open a workspace.
2. View registered agents.
3. Submit a customer issue.
4. Watch multiple agents process it.
5. See memories created and retrieved.
6. View the full task activity timeline.
7. Approve or reject the final output.
8. Resume the task later with context intact.

Current status: all MVP success criteria are implemented.

## Remaining Essential Work

These are the remaining important steps before calling this a presentable MVP release:

1. Verify setup from a fresh clone and fresh database.
2. Deploy the FastAPI app and managed PostgreSQL database.
3. Run Alembic migrations in the deployed environment.
4. Smoke-test `/dashboard`, `/workflows/demo-bootstrap`, `/tasks/{task_id}/context-packet`, and `/system/status` after deploy.
5. Tag the release as `v0.1.0-mvp`.

## Deferred Until After MVP

These are intentionally not required for the MVP:

- Enterprise authentication and SSO.
- Billing.
- Complex RBAC.
- External integrations.
- Agent marketplace.
- Kubernetes.
- Mobile app.
- Full separate frontend replacement for the Python dashboard.
