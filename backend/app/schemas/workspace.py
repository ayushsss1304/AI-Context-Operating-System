from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class WorkspaceCreate(SQLModel):
    name: str
    description: str | None = None


class WorkspaceRead(WorkspaceCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
