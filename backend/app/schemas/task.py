from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


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
