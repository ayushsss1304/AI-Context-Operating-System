from fastapi import HTTPException
from sqlmodel import Session, select
from uuid import UUID

from app.models.activity import Activity
from app.models.agent import Agent
from app.models.approval import Approval
from app.models.memory import Memory
from app.models.task import Task
from app.schemas.memory import MemorySearchRequest
from app.services.memory_service import MemoryService
from app.services.timeline_service import build_handoff_trace


def build_task_context_packet(
    session: Session,
    task_id: UUID,
    memory_service: MemoryService | None = None,
) -> dict:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    agents = session.exec(select(Agent).where(Agent.workspace_id == task.workspace_id)).all()
    agents_by_id = {str(agent.id): agent for agent in agents}
    current_owner = agents_by_id.get(str(task.current_owner_agent_id)) if task.current_owner_agent_id else None

    activities = session.exec(
        select(Activity)
        .where(Activity.workspace_id == task.workspace_id, Activity.task_id == task.id)
        .order_by(Activity.created_at.asc())
    ).all()
    approvals = session.exec(
        select(Approval)
        .where(Approval.workspace_id == task.workspace_id, Approval.task_id == task.id)
        .order_by(Approval.created_at.desc())
    ).all()

    query = f"{task.title} {task.description or ''}".strip()
    memory_client = memory_service or MemoryService()
    relevant_memories = memory_client.search(
        session,
        MemorySearchRequest(
            workspace_id=task.workspace_id,
            query=query,
            limit=5,
        ),
    )
    if not relevant_memories:
        relevant_memories = session.exec(
            select(Memory)
            .where(Memory.workspace_id == task.workspace_id)
            .order_by(Memory.created_at.desc())
            .limit(5)
        ).all()

    handoff_trace = build_handoff_trace(activities, agents_by_id)
    resume_summary = _build_resume_summary(task, current_owner, relevant_memories, approvals, handoff_trace)

    return {
        "task": task,
        "current_owner": current_owner,
        "relevant_memories": relevant_memories,
        "approvals": approvals,
        "handoff_trace": handoff_trace,
        "resume_summary": resume_summary,
    }


def _build_resume_summary(
    task: Task,
    current_owner: Agent | None,
    memories: list[Memory],
    approvals: list[Approval],
    handoff_trace: list[dict[str, str]],
) -> str:
    owner_name = current_owner.name if current_owner else "unassigned"
    pending_approvals = [approval for approval in approvals if approval.status == "pending"]
    approval_text = (
        f"{len(pending_approvals)} pending approval"
        if len(pending_approvals) == 1
        else f"{len(pending_approvals)} pending approvals"
    )
    return (
        f"Task '{task.title}' is {task.status} and currently owned by {owner_name}. "
        f"It has {len(memories)} relevant memories, {len(handoff_trace)} handoff events, and {approval_text}."
    )
