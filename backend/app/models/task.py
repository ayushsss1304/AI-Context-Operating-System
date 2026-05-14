from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    title: str = Field(index=True, max_length=180)
    description: str | None = None
    status: str = Field(default="pending", index=True, max_length=40)
    current_owner_agent_id: UUID | None = Field(default=None, foreign_key="agent.id", index=True)
    priority: str = Field(default="medium", max_length=40)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
