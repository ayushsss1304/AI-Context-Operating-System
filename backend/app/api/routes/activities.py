from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityRead

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("", response_model=ActivityRead)
def create_activity(payload: ActivityCreate, session: Session = Depends(get_session)) -> Activity:
    activity = Activity.model_validate(payload)
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity


@router.get("", response_model=list[ActivityRead])
def list_activities(
    workspace_id: UUID | None = Query(default=None),
    task_id: UUID | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[Activity]:
    statement = select(Activity)
    if workspace_id:
        statement = statement.where(Activity.workspace_id == workspace_id)
    if task_id:
        statement = statement.where(Activity.task_id == task_id)
    return list(session.exec(statement).all())
