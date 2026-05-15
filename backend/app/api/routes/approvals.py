from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.activity import Activity
from app.models.approval import Approval
from app.models.task import Task
from app.schemas.approval import ApprovalCreate, ApprovalRead, ApprovalReview

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("", response_model=ApprovalRead)
def create_approval(payload: ApprovalCreate, session: Session = Depends(get_session)) -> Approval:
    approval = Approval.model_validate(payload)
    session.add(approval)
    session.commit()
    session.refresh(approval)
    return approval


@router.get("", response_model=list[ApprovalRead])
def list_approvals(
    workspace_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[Approval]:
    statement = select(Approval)
    if workspace_id:
        statement = statement.where(Approval.workspace_id == workspace_id)
    if status:
        statement = statement.where(Approval.status == status)
    return list(session.exec(statement).all())


@router.post("/{approval_id}/approve", response_model=ApprovalRead)
def approve(approval_id: UUID, payload: ApprovalReview, session: Session = Depends(get_session)) -> Approval:
    return review_approval(approval_id, "approved", payload.reviewed_by, session)


@router.post("/{approval_id}/reject", response_model=ApprovalRead)
def reject(approval_id: UUID, payload: ApprovalReview, session: Session = Depends(get_session)) -> Approval:
    return review_approval(approval_id, "rejected", payload.reviewed_by, session)


def review_approval(approval_id: UUID, status: str, reviewed_by: str, session: Session) -> Approval:
    approval = session.get(Approval, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval.status = status
    approval.reviewed_by = reviewed_by
    approval.reviewed_at = datetime.utcnow()
    session.add(approval)

    task = session.get(Task, approval.task_id)
    if task:
        task.status = "approved" if status == "approved" else "rejected"
        task.updated_at = datetime.utcnow()
        session.add(task)

    session.add(
        Activity(
            workspace_id=approval.workspace_id,
            task_id=approval.task_id,
            action_type="approval_reviewed",
            input_summary=approval.title,
            output_summary=f"{reviewed_by} {status} the recommendation.",
            full_output=approval.content,
            status=status,
        )
    )
    session.commit()
    session.refresh(approval)
    return approval
