from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from app.schemas.activity import ActivityRead
from app.schemas.agent import AgentRead
from app.schemas.approval import ApprovalRead
from app.schemas.memory import MemoryRead
from app.schemas.timeline import HandoffTraceItem


class TaskCreate(SQLModel):
    workspace_id: UUID
    title: str
    description: str | None = None
    current_owner_agent_id: UUID | None = None
    priority: str = "medium"


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    current_owner_agent_id: UUID | None = None
    priority: str | None = None


class TaskRead(TaskCreate):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime


class TaskContextPacket(SQLModel):
    task: TaskRead
    current_owner: AgentRead | None = None
    relevant_memories: list[MemoryRead]
    approvals: list[ApprovalRead]
    handoff_trace: list[HandoffTraceItem]
    resume_summary: str


class TaskContinuationRequest(SQLModel):
    agent_id: UUID
    instruction: str


class TaskContinuationResponse(SQLModel):
    task: TaskRead
    memory: MemoryRead
    activity: ActivityRead
    context_packet: TaskContextPacket
