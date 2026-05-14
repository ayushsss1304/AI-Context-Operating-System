from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.workflow import CustomerIssueDemoRequest, CustomerIssueDemoResponse
from app.services.workflow_service import run_customer_issue_demo

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/customer-issue-demo", response_model=CustomerIssueDemoResponse)
def customer_issue_demo(
    payload: CustomerIssueDemoRequest,
    session: Session = Depends(get_session),
) -> dict:
    return run_customer_issue_demo(session, payload)
