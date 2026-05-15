from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceOverview, WorkspaceRead
from app.services.workspace_overview_service import build_workspace_overview
from app.services.workflow_service import ensure_demo_agents

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceRead)
def create_workspace(payload: WorkspaceCreate, session: Session = Depends(get_session)) -> Workspace:
    workspace = Workspace.model_validate(payload)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    ensure_demo_agents(session, workspace.id)
    return workspace


@router.get("", response_model=list[WorkspaceRead])
def list_workspaces(session: Session = Depends(get_session)) -> list[Workspace]:
    return list(session.exec(select(Workspace)).all())


@router.get("/{workspace_id}", response_model=WorkspaceRead)
def get_workspace(workspace_id: UUID, session: Session = Depends(get_session)) -> Workspace:
    workspace = session.get(Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.get("/{workspace_id}/overview", response_model=WorkspaceOverview)
def get_workspace_overview(workspace_id: UUID, session: Session = Depends(get_session)) -> dict:
    return build_workspace_overview(session, workspace_id)
