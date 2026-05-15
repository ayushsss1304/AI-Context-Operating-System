from app.models.activity import Activity
from app.models.workspace import Workspace
from app.schemas.workflow import CustomerIssueDemoRequest
from app.services import workflow_service


class FakeLLMService:
    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if "Support Agent" in system_prompt:
            return "Customer reports dashboard filters disappear after browser refresh."
        if "Engineering Agent" in system_prompt:
            return "Engineering should inspect persistence, client storage, and settings save APIs."
        if "Product Agent" in system_prompt:
            return "This affects user trust and should be approved for technical investigation."
        return fallback


def test_customer_issue_workflow_creates_expected_records(session, monkeypatch):
    monkeypatch.setattr(workflow_service, "LLMService", FakeLLMService)
    workspace = Workspace(name="Workflow Test", description="Shared memory workflow")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    result = workflow_service.run_customer_issue_demo(
        session,
        CustomerIssueDemoRequest(
            workspace_id=workspace.id,
            customer_name="WorkflowCo",
            issue="Saved dashboard filters disappear after browser refresh.",
        ),
    )

    assert result["task"].status == "waiting_for_approval"
    assert len(result["memories"]) == 3
    assert all(memory.embedding for memory in result["memories"])
    assert len(result["activities"]) == 5
    assert result["approval"].status == "pending"
    assert [item["actor"] for item in result["handoff_trace"]] == [
        "Support Agent",
        "Engineering Agent",
        "Engineering Agent",
        "Product Agent",
        "Manager Agent",
    ]
    assert result["handoff_trace"][0]["label"] == "Stored shared memory"


def test_demo_agents_are_idempotently_registered(session):
    workspace = Workspace(name="Agent Registry Test", description="Demo agents")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    first_registration = workflow_service.ensure_demo_agents(session, workspace.id)
    second_registration = workflow_service.ensure_demo_agents(session, workspace.id)

    assert set(first_registration) == {
        "Support Agent",
        "Engineering Agent",
        "Product Agent",
        "Manager Agent",
    }
    assert len(second_registration) == 4
    assert first_registration["Support Agent"].id == second_registration["Support Agent"].id


def test_engineering_agent_retrieves_support_memory_from_store(session, monkeypatch):
    monkeypatch.setattr(workflow_service, "LLMService", FakeLLMService)
    workspace = Workspace(name="Retrieval Test", description="Shared memory retrieval")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    result = workflow_service.run_customer_issue_demo(
        session,
        CustomerIssueDemoRequest(
            workspace_id=workspace.id,
            customer_name="RetrievalCo",
            issue="Saved dashboard filters disappear after browser refresh.",
        ),
    )

    retrieval = next(
        activity for activity in result["activities"] if activity.action_type == "memory_retrieved"
    )

    assert retrieval.input_summary.startswith("Search query:")
    assert retrieval.output_summary == "Customer issue - RetrievalCo"

    stored_retrieval = session.get(Activity, retrieval.id)
    assert stored_retrieval is not None
    assert stored_retrieval.output_summary == "Customer issue - RetrievalCo"
