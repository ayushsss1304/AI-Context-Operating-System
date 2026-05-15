from sqlmodel import Session, select

from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemorySearchRequest
from app.services.embedding_service import EmbeddingService


class MemoryService:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or EmbeddingService()

    def create(self, session: Session, payload: MemoryCreate) -> Memory:
        memory = Memory.model_validate(payload)
        memory.embedding = self.embedding_service.embed(self._embedding_text(memory))
        session.add(memory)
        session.commit()
        session.refresh(memory)
        return memory

    def search(self, session: Session, payload: MemorySearchRequest) -> list[Memory]:
        query = payload.query.strip()
        query_lower = query.lower()
        query_embedding = self.embedding_service.embed(query)

        statement = select(Memory).where(Memory.workspace_id == payload.workspace_id)
        memories = session.exec(statement).all()

        scored = []
        for memory in memories:
            semantic_score = self.embedding_service.similarity(query_embedding, memory.embedding)
            keyword_score = self._keyword_score(query_lower, memory)
            score = semantic_score + keyword_score
            if score > 0:
                scored.append((score, memory))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [memory for _, memory in scored[: payload.limit]]

    def _embedding_text(self, memory: Memory) -> str:
        tags = " ".join(memory.tags)
        return f"{memory.title}\n{memory.memory_type}\n{tags}\n{memory.content}"

    def _keyword_score(self, query: str, memory: Memory) -> float:
        if not query:
            return 0.0

        score = 0.0
        if query in memory.title.lower():
            score += 0.5
        if query in memory.content.lower():
            score += 0.35
        if any(query in tag.lower() for tag in memory.tags):
            score += 0.25
        return score
