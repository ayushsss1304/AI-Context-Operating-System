from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentRead

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentRead)
def create_agent(payload: AgentCreate, session: Session = Depends(get_session)) -> Agent:
    agent = Agent.model_validate(payload)
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


@router.get("", response_model=list[AgentRead])
def list_agents(
    workspace_id: UUID | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[Agent]:
    statement = select(Agent)
    if workspace_id:
        statement = statement.where(Agent.workspace_id == workspace_id)
    return list(session.exec(statement).all())


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: UUID, session: Session = Depends(get_session)) -> Agent:
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
