from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.task import Task
from app.schemas.task import (
    TaskContextPacket,
    TaskContinuationRequest,
    TaskContinuationResponse,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from app.services.context_packet_service import build_task_context_packet
from app.services.task_continuation_service import continue_task_from_context

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead)
def create_task(payload: TaskCreate, session: Session = Depends(get_session)) -> Task:
    task = Task.model_validate(payload)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    workspace_id: UUID | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[Task]:
    statement = select(Task)
    if workspace_id:
        statement = statement.where(Task.workspace_id == workspace_id)
    return list(session.exec(statement).all())


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: UUID, session: Session = Depends(get_session)) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}/context-packet", response_model=TaskContextPacket)
def get_task_context_packet(task_id: UUID, session: Session = Depends(get_session)) -> dict:
    return build_task_context_packet(session, task_id)


@router.post("/{task_id}/continue", response_model=TaskContinuationResponse)
def continue_task(
    task_id: UUID,
    payload: TaskContinuationRequest,
    session: Session = Depends(get_session),
) -> dict:
    return continue_task_from_context(session, task_id, payload.agent_id, payload.instruction)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: UUID, payload: TaskUpdate, session: Session = Depends(get_session)) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
