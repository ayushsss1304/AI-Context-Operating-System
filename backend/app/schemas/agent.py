from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class AgentCreate(SQLModel):
    workspace_id: UUID
    name: str
    role: str
    description: str | None = None
    capabilities: list[str] = []
    permissions: list[str] = []


class AgentRead(AgentCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
