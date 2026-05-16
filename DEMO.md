# AI Context OS MVP Demo Script

Use this script to show the MVP end to end.

## Start

```bash
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```txt
http://127.0.0.1:8000/dashboard
```

## Demo Flow

1. Click **Create Full Demo**.
   - The demo uses a Panasonic-style Smart TV firmware escalation.
   - The production issue is Wi-Fi disconnects after firmware v4.18.2 on MX800 and MX950 models.
2. Show **Demo Summary**.
   - It should show the active task status, owner, memories, events, and current step.
3. Show **Agent Registry**.
   - Support Agent
   - Engineering Agent
   - Product Agent
   - Manager Agent
4. Show **Handoff Timeline**.
   - Support stores shared memory.
   - Engineering retrieves context.
   - Engineering creates an investigation note.
   - Product creates impact summary.
   - Manager requests approval.
5. Show **Shared Memory**.
   - Confirm seeded prior incident, QA playbook, release policy, support, engineering, and product memories exist.
6. Open **Context packet** from Task Detail.
   - This proves the task can be resumed later with owner, memories, approvals, and handoff trace.
7. Use **Continue Task**.
   - Choose Engineering Agent.
   - Submit the default continuation instruction.
   - Confirm the handoff timeline adds **Continued task**.
8. Use **Review Note** under Approval.
   - Add a short reason.
   - Click Approve or Reject.
   - Confirm the task status changes and the activity timeline records the review.
9. Open **System Status**.
   - Confirm the system status is `ready`.

## API Shortcut

Create a full demo with one API call:

```bash
curl -X POST http://127.0.0.1:8000/workflows/demo-bootstrap ^
  -H "Content-Type: application/json" ^
  -d "{\"workspace_name\":\"Panasonic Smart TV Reliability Desk\",\"customer_name\":\"Panasonic Support Escalation - Europe Smart TV Line\",\"issue\":\"After firmware v4.18.2 shipped to Panasonic MX800 and MX950 Smart TV models in Germany and the UK, customers report Wi-Fi disconnects within 10 to 20 minutes of opening Netflix or YouTube.\"}"
```

Then check readiness:

```bash
curl http://127.0.0.1:8000/system/status
```
