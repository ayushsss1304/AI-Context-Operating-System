from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.core.database import get_session
from app.api.routes.approvals import review_approval
from app.models.activity import Activity
from app.models.agent import Agent
from app.models.approval import Approval
from app.models.memory import Memory
from app.models.task import Task
from app.models.workspace import Workspace
from app.schemas.memory import MemorySearchRequest
from app.schemas.workflow import CustomerIssueDemoRequest, DemoBootstrapRequest
from app.services.memory_service import MemoryService
from app.services.task_continuation_service import continue_task_from_context
from app.services.timeline_service import build_handoff_trace
from app.api.routes.workflows import demo_bootstrap
from app.services.workflow_service import ensure_demo_agents, run_customer_issue_demo

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/dashboard")
def dashboard(
    request: Request,
    workspace_id: UUID | None = None,
    task_id: UUID | None = None,
    memory_query: str = "",
    session: Session = Depends(get_session),
):
    workspaces = session.exec(select(Workspace).order_by(Workspace.created_at.desc())).all()
    active_workspace_id = workspace_id or (workspaces[0].id if workspaces else None)

    memories: list[Memory] = []
    activities: list[Activity] = []
    approvals: list[Approval] = []
    agents: list[Agent] = []
    agents_by_id: dict[str, Agent] = {}
    tasks: list[Task] = []
    active_task: Task | None = None
    task_activities: list[Activity] = []
    task_approvals: list[Approval] = []
    timeline_items: list[dict[str, str]] = []

    if active_workspace_id:
        agents = session.exec(
            select(Agent)
            .where(Agent.workspace_id == active_workspace_id)
            .order_by(Agent.created_at.asc())
        ).all()
        agents_by_id = {str(agent.id): agent for agent in agents}
        tasks = session.exec(
            select(Task)
            .where(Task.workspace_id == active_workspace_id)
            .order_by(Task.created_at.desc())
        ).all()
        active_task = session.get(Task, task_id) if task_id else (tasks[0] if tasks else None)

        if memory_query.strip():
            memories = MemoryService().search(
                session,
                MemorySearchRequest(
                    workspace_id=active_workspace_id,
                    query=memory_query,
                    limit=20,
                ),
            )
        else:
            memories = session.exec(
                select(Memory)
                .where(Memory.workspace_id == active_workspace_id)
                .order_by(Memory.created_at.desc())
            ).all()
        activities = session.exec(
            select(Activity)
            .where(Activity.workspace_id == active_workspace_id)
            .order_by(Activity.created_at.desc())
        ).all()
        approvals = session.exec(
            select(Approval)
            .where(Approval.workspace_id == active_workspace_id)
            .order_by(Approval.created_at.desc())
        ).all()
        if active_task:
            task_activities = [activity for activity in activities if activity.task_id == active_task.id]
            task_approvals = [approval for approval in approvals if approval.task_id == active_task.id]
            timeline_items = build_handoff_trace(task_activities, agents_by_id)
        else:
            timeline_items = build_handoff_trace(activities, agents_by_id)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "workspaces": workspaces,
            "active_workspace_id": str(active_workspace_id) if active_workspace_id else "",
            "tasks": tasks,
            "active_task": active_task,
            "active_task_id": str(active_task.id) if active_task else "",
            "task_activities": task_activities,
            "task_approvals": task_approvals,
            "timeline_items": timeline_items,
            "agents": agents,
            "agents_by_id": agents_by_id,
            "memories": memories,
            "memory_query": memory_query,
            "activities": activities,
            "approvals": approvals,
            "pending_approval": next((approval for approval in approvals if approval.status == "pending"), None),
        },
    )


@router.post("/dashboard/workspaces")
def create_dashboard_workspace(
    name: str = Form(...),
    description: str = Form(""),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    workspace = Workspace(name=name, description=description)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    ensure_demo_agents(session, workspace.id)
    return RedirectResponse(url=f"/dashboard?workspace_id={workspace.id}", status_code=303)


@router.post("/dashboard/demo-bootstrap")
def bootstrap_dashboard_demo(
    workspace_name: str = Form("Demo Company"),
    customer_name: str = Form("Acme SaaS"),
    issue: str = Form("Users report that dashboard settings disappear after refreshing the page."),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    result = demo_bootstrap(
        DemoBootstrapRequest(
            workspace_name=workspace_name,
            workspace_description="AI Context OS one-click demo workspace",
            customer_name=customer_name,
            issue=issue,
        ),
        session,
    )
    workspace_id = result["overview"]["workspace"].id
    task_id = result["workflow"]["task"].id
    return RedirectResponse(url=f"/dashboard?workspace_id={workspace_id}&task_id={task_id}", status_code=303)


@router.post("/dashboard/workflows/customer-issue-demo")
def run_dashboard_workflow(
    workspace_id: UUID = Form(...),
    customer_name: str = Form(...),
    issue: str = Form(...),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    run_customer_issue_demo(
        session,
        CustomerIssueDemoRequest(
            workspace_id=workspace_id,
            customer_name=customer_name,
            issue=issue,
        ),
    )
    return RedirectResponse(url=f"/dashboard?workspace_id={workspace_id}", status_code=303)


@router.post("/dashboard/tasks/{task_id}/continue")
def continue_dashboard_task(
    task_id: UUID,
    workspace_id: UUID = Form(...),
    agent_id: UUID = Form(...),
    instruction: str = Form(...),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    continue_task_from_context(session, task_id, agent_id, instruction)
    return RedirectResponse(url=f"/dashboard?workspace_id={workspace_id}&task_id={task_id}", status_code=303)


@router.post("/dashboard/approvals/{approval_id}/approve")
def approve_dashboard_output(
    approval_id: UUID,
    workspace_id: UUID = Form(...),
    reviewed_by: str = Form("Ayush"),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    review_approval(approval_id, "approved", reviewed_by, session)
    return RedirectResponse(url=f"/dashboard?workspace_id={workspace_id}", status_code=303)


@router.post("/dashboard/approvals/{approval_id}/reject")
def reject_dashboard_output(
    approval_id: UUID,
    workspace_id: UUID = Form(...),
    reviewed_by: str = Form("Ayush"),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    review_approval(approval_id, "rejected", reviewed_by, session)
    return RedirectResponse(url=f"/dashboard?workspace_id={workspace_id}", status_code=303)
