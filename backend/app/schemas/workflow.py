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
    customer_name: str = "Demo Customer"
    issue: str


class CustomerIssueDemoResponse(SQLModel):
    task: TaskRead
    memories: list[MemoryRead]
    activities: list[ActivityRead]
    approval: ApprovalRead
    handoff_trace: list[HandoffTraceItem]


class DemoBootstrapRequest(SQLModel):
    workspace_name: str = "Panasonic Smart TV Reliability Desk"
    workspace_description: str | None = (
        "Shared AI workspace for connected TV support, QA, firmware, product, and release decisions."
    )
    customer_name: str = "Panasonic Support Escalation - Europe Smart TV Line"
    issue: str = (
        "After firmware v4.18.2 shipped to Panasonic MX800 and MX950 Smart TV models in Germany and the UK, "
        "customers report Wi-Fi disconnects within 10 to 20 minutes of opening Netflix or YouTube. Support has "
        "42 tickets in 36 hours, mostly from dual-band home routers. Rebooting the TV temporarily restores the "
        "connection, but the issue returns after streaming resumes."
    )


class DemoBootstrapResponse(SQLModel):
    workflow: CustomerIssueDemoResponse
    overview: WorkspaceOverview
