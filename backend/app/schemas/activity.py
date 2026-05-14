from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class ActivityCreate(SQLModel):
    workspace_id: UUID
    task_id: UUID | None = None
    agent_id: UUID | None = None
    action_type: str
    input_summary: str | None = None
    output_summary: str | None = None
    full_output: str | None = None
    status: str = "completed"


class ActivityRead(ActivityCreate):
    id: UUID
    created_at: datetime
