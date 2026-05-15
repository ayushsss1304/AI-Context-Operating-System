from app.models.workspace import Workspace
from app.schemas.memory import MemoryCreate, MemorySearchRequest
from app.services.memory_service import MemoryService


def test_memory_search_ranks_relevant_memory_first(session):
    workspace = Workspace(name="Search Test", description="Semantic memory search")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    service = MemoryService()
    dashboard_memory = service.create(
        session,
        MemoryCreate(
            workspace_id=workspace.id,
            title="Dashboard preferences lost",
            content="Users lose saved dashboard settings after refreshing the page.",
            memory_type="customer_issue",
            tags=["dashboard", "settings"],
            importance_score=0.9,
        ),
    )
    service.create(
        session,
        MemoryCreate(
            workspace_id=workspace.id,
            title="Invoice export delay",
            content="Finance users report CSV invoice exports are slow during month end.",
            memory_type="customer_issue",
            tags=["billing", "export"],
        ),
    )

    results = service.search(
        session,
        MemorySearchRequest(
            workspace_id=workspace.id,
            query="saved settings disappear after reload",
            limit=2,
        ),
    )

    assert results[0].id == dashboard_memory.id
    assert len(results[0].embedding or []) == 384
