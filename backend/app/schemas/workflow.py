from uuid import UUID

from sqlmodel import SQLModel

from app.schemas.activity import ActivityRead
from app.schemas.approval import ApprovalRead
from app.schemas.memory import MemoryRead
from app.schemas.task import TaskRead


class CustomerIssueDemoRequest(SQLModel):
    workspace_id: UUID
    customer_name: str = "Demo Customer"
    issue: str


class CustomerIssueDemoResponse(SQLModel):
    task: TaskRead
    memories: list[MemoryRead]
    activities: list[ActivityRead]
    approval: ApprovalRead
