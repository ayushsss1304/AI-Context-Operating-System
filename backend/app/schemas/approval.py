from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class ApprovalCreate(SQLModel):
    workspace_id: UUID
    task_id: UUID
    requested_by_agent_id: UUID | None = None
    title: str
    content: str


class ApprovalReview(SQLModel):
    reviewed_by: str
    review_note: str | None = None


class ApprovalRead(ApprovalCreate):
    id: UUID
    status: str
    reviewed_by: str | None = None
    review_note: str | None = None
    created_at: datetime
    reviewed_at: datetime | None = None
