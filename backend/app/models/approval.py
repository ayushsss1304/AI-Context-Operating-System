from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Approval(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    task_id: UUID = Field(foreign_key="task.id", index=True)
    requested_by_agent_id: UUID | None = Field(default=None, foreign_key="agent.id", index=True)
    title: str = Field(max_length=180)
    content: str
    status: str = Field(default="pending", index=True, max_length=40)
    reviewed_by: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: datetime | None = None
