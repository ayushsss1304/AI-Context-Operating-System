from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryRead, MemorySearchRequest

router = APIRouter(prefix="/memories", tags=["memories"])


@router.post("", response_model=MemoryRead)
def create_memory(payload: MemoryCreate, session: Session = Depends(get_session)) -> Memory:
    memory = Memory.model_validate(payload)
    session.add(memory)
    session.commit()
    session.refresh(memory)
    return memory


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
    query = payload.query.lower().strip()
    statement = select(Memory).where(Memory.workspace_id == payload.workspace_id)
    memories = session.exec(statement).all()
    matches = [
        memory
        for memory in memories
        if query in memory.title.lower()
        or query in memory.content.lower()
        or any(query in tag.lower() for tag in memory.tags)
    ]
    return matches[: payload.limit]


@router.get("/{memory_id}", response_model=MemoryRead)
def get_memory(memory_id: UUID, session: Session = Depends(get_session)) -> Memory:
    memory = session.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory
