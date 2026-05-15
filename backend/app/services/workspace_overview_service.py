from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.activity import Activity
from app.models.agent import Agent
from app.models.approval import Approval
from app.models.memory import Memory
from app.models.task import Task
from app.models.workspace import Workspace
from app.services.timeline_service import build_handoff_trace


def build_workspace_overview(session: Session, workspace_id: UUID) -> dict:
    workspace = session.get(Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    agents = session.exec(
        select(Agent)
        .where(Agent.workspace_id == workspace_id)
        .order_by(Agent.created_at.asc())
    ).all()
    tasks = session.exec(
        select(Task)
        .where(Task.workspace_id == workspace_id)
        .order_by(Task.created_at.desc())
    ).all()
    memories = session.exec(
        select(Memory)
        .where(Memory.workspace_id == workspace_id)
        .order_by(Memory.created_at.desc())
    ).all()
    approvals = session.exec(
        select(Approval)
        .where(Approval.workspace_id == workspace_id)
        .order_by(Approval.created_at.desc())
    ).all()

    active_task = tasks[0] if tasks else None
    task_activities = []
    if active_task:
        task_activities = session.exec(
            select(Activity)
            .where(Activity.workspace_id == workspace_id, Activity.task_id == active_task.id)
            .order_by(Activity.created_at.asc())
        ).all()

    return {
        "workspace": workspace,
        "agents": agents,
        "tasks": tasks,
        "memories": memories,
        "approvals": approvals,
        "active_task": active_task,
        "handoff_trace": build_handoff_trace(
            task_activities,
            {str(agent.id): agent for agent in agents},
        ),
    }
