from uuid import UUID

from sqlmodel import SQLModel

from app.schemas.activity import ActivityRead
from app.schemas.approval import ApprovalRead
from app.schemas.memory import MemoryRead
from app.schemas.task import TaskRead
from app.schemas.timeline import HandoffTraceItem
from app.schemas.workspace import WorkspaceOverview


class CustomerIssueDemoRequest(SQLModel):
    workspace_id: UUID
    customer_name: str = "SMT Line 3"
    issue: str


FactoryIssueDemoRequest = CustomerIssueDemoRequest


class CustomerIssueDemoResponse(SQLModel):
    task: TaskRead
    memories: list[MemoryRead]
    activities: list[ActivityRead]
    approval: ApprovalRead
    handoff_trace: list[HandoffTraceItem]


class DemoBootstrapRequest(SQLModel):
    workspace_name: str = "Panasonic Smart Factory Pilot"
    workspace_description: str | None = "Factory issue-resolution pilot for workforce continuity"
    customer_name: str = "SMT Line 3"
    issue: str = (
        "An SMT line starts showing intermittent solder defects after a material changeover. "
        "Operators see higher rework during the evening shift and need maintenance, quality, "
        "and plant management to align on next action."
    )


class DemoBootstrapResponse(SQLModel):
    workflow: CustomerIssueDemoResponse
    overview: WorkspaceOverview
