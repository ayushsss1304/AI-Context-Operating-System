from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryRead, MemorySearchRequest
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/memories", tags=["memories"])


@router.post("", response_model=MemoryRead)
def create_memory(payload: MemoryCreate, session: Session = Depends(get_session)) -> Memory:
    return MemoryService().create(session, payload)


@router.get("", response_model=list[MemoryRead])
def list_memories(
    workspace_id: UUID | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[Memory]:
    statement = select(Memory)
    if workspace_id:
        statement = statement.where(Memory.workspace_id == workspace_id)
    return list(session.exec(statement).all())


@router.post("/search", response_model=list[MemoryRead])
def search_memories(payload: MemorySearchRequest, session: Session = Depends(get_session)) -> list[Memory]:
    return MemoryService().search(session, payload)


@router.get("/{memory_id}", response_model=MemoryRead)
def get_memory(memory_id: UUID, session: Session = Depends(get_session)) -> Memory:
    memory = session.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory
