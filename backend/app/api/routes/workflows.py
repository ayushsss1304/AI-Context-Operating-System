from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.models.workspace import Workspace
from app.schemas.workflow import (
    CustomerIssueDemoRequest,
    CustomerIssueDemoResponse,
    DemoBootstrapRequest,
    DemoBootstrapResponse,
)
from app.services.workspace_overview_service import build_workspace_overview
from app.services.workflow_service import run_customer_issue_demo

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/customer-issue-demo", response_model=CustomerIssueDemoResponse)
def customer_issue_demo(
    payload: CustomerIssueDemoRequest,
    session: Session = Depends(get_session),
) -> dict:
    return run_customer_issue_demo(session, payload)


@router.post("/demo-bootstrap", response_model=DemoBootstrapResponse)
def demo_bootstrap(
    payload: DemoBootstrapRequest,
    session: Session = Depends(get_session),
) -> dict:
    workspace = Workspace(
        name=payload.workspace_name,
        description=payload.workspace_description,
    )
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    workflow = run_customer_issue_demo(
        session,
        CustomerIssueDemoRequest(
            workspace_id=workspace.id,
            customer_name=payload.customer_name,
            issue=payload.issue,
        ),
    )
    return {
        "workflow": workflow,
        "overview": build_workspace_overview(session, workspace.id),
    }
