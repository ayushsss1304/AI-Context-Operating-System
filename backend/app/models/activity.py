from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Activity(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    task_id: UUID | None = Field(default=None, foreign_key="task.id", index=True)
    agent_id: UUID | None = Field(default=None, foreign_key="agent.id", index=True)
    action_type: str = Field(index=True, max_length=80)
    input_summary: str | None = None
    output_summary: str | None = None
    full_output: str | None = None
    status: str = Field(default="completed", index=True, max_length=40)
    created_at: datetime = Field(default_factory=datetime.utcnow)
