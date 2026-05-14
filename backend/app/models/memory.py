from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Memory(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", index=True)
    created_by_agent_id: UUID | None = Field(default=None, foreign_key="agent.id", index=True)
    title: str = Field(index=True, max_length=180)
    content: str
    memory_type: str = Field(index=True, max_length=80)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    embedding: list[float] | None = Field(default=None, sa_column=Column(JSON))
    source: str | None = None
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
