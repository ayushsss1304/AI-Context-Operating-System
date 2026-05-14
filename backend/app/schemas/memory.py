from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class MemoryCreate(SQLModel):
    workspace_id: UUID
    created_by_agent_id: UUID | None = None
    title: str
    content: str
    memory_type: str
    tags: list[str] = []
    source: str | None = None
    importance_score: float = 0.5


class MemoryRead(MemoryCreate):
    id: UUID
    embedding: list[float] | None = None
    created_at: datetime
    updated_at: datetime


class MemorySearchRequest(SQLModel):
    workspace_id: UUID
    query: str
    limit: int = 10
