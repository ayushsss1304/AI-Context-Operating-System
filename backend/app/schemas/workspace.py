from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from app.schemas.agent import AgentRead
from app.schemas.approval import ApprovalRead
from app.schemas.memory import MemoryRead
from app.schemas.task import TaskRead
from app.schemas.timeline import HandoffTraceItem


class WorkspaceCreate(SQLModel):
    name: str
    description: str | None = None


class WorkspaceRead(WorkspaceCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime


class WorkspaceOverview(SQLModel):
    workspace: WorkspaceRead
    agents: list[AgentRead]
    tasks: list[TaskRead]
    memories: list[MemoryRead]
    approvals: list[ApprovalRead]
    active_task: TaskRead | None = None
    handoff_trace: list[HandoffTraceItem]
