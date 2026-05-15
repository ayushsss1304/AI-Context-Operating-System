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
    workspace_name: str = "Demo Company"
    workspace_description: str | None = "AI Context OS demo workspace"
    customer_name: str = "Acme SaaS"
    issue: str = "Users report that dashboard settings disappear after refreshing the page."


class DemoBootstrapResponse(SQLModel):
    workflow: CustomerIssueDemoResponse
    overview: WorkspaceOverview
