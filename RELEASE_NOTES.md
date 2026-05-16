# Release Notes

## v0.1.0-mvp

AI Context OS MVP proves shared memory, workflow continuity, multi-agent handoff, and human oversight in a single backend-first demo.

### Included

- FastAPI backend with Python-rendered dashboard.
- Workspace, agent registry, shared memory, task, activity, and approval modules.
- LangGraph customer issue workflow.
- Support, Engineering, Product, and Manager demo agents.
- Shared memory write and retrieval.
- Handoff timeline.
- Human approval and rejection with manager review notes.
- Task context packet for workflow continuity.
- Task continuation endpoint.
- One-call demo bootstrap.
- System readiness endpoint.
- Alembic migrations.
- Backend test suite.
- Optional Next.js frontend scaffold.

### Verification

Completed on May 16, 2026:

- Fresh clone compile check passed.
- Fresh clone backend tests passed: `15 passed`.
- Fresh database Alembic migration passed from empty DB.
- Fresh runtime smoke test passed:
  - `GET /health`
  - `POST /workflows/demo-bootstrap`
  - `GET /system/status`

### Deferred

- Enterprise authentication.
- Billing.
- Complex RBAC.
- External integrations.
- Agent marketplace.
- Full production frontend replacement.

## v0.1.1-deploy-ready

Deployment readiness update for the MVP.

### Added

- Render Blueprint deployment file: `render.yaml`.
- Managed Postgres deployment notes.
- Database URL normalization for hosted Postgres URLs such as `postgres://...` and `postgresql://...`.
- Tests for database URL normalization.

### Verification

- Backend tests passed: `18 passed`.
- Fresh Alembic migration check passed.

## v0.1.2-realistic-demo-data

Realistic product-company demo data update.

### Added

- Panasonic-style Smart TV reliability demo workspace.
- Firmware v4.18.2 Wi-Fi disconnect escalation scenario.
- Seeded prior incident memory for MX700 Wi-Fi reconnect regression.
- Seeded QA reproduction playbook for streaming connectivity regressions.
- Seeded release policy memory for connected TV hotfix thresholds.

### Verification

- Backend tests passed: `18 passed`.
- Local demo bootstrap smoke test confirmed 4 agents, 6 memories, and a pending approval.
