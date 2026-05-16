from app.models.activity import Activity
from app.models.workspace import Workspace
from app.schemas.workflow import CustomerIssueDemoRequest
from app.services import workflow_service


class FakeLLMService:
    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if "Line Production Agent" in system_prompt:
            return "Operators report intermittent solder defects after material changeover."
        if "Maintenance Engineering Agent" in system_prompt:
            return "Maintenance should inspect material changeover records, solder profile history, and feeder setup."
        if "Quality Process Agent" in system_prompt:
            return "Quality should treat this as a rework and defect-risk issue requiring controlled action."
        return fallback


def test_factory_issue_workflow_creates_expected_records(session, monkeypatch):
    monkeypatch.setattr(workflow_service, "LLMService", FakeLLMService)
    workspace = Workspace(name="Workflow Test", description="Shared memory workflow")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    result = workflow_service.run_customer_issue_demo(
        session,
        CustomerIssueDemoRequest(
            workspace_id=workspace.id,
            customer_name="SMT Line 3",
            issue="Intermittent solder defects appear after material changeover.",
        ),
    )

    assert result["task"].status == "waiting_for_approval"
    assert len(result["memories"]) == 3
    assert all(memory.embedding for memory in result["memories"])
    assert len(result["activities"]) == 5
    assert result["approval"].status == "pending"
    assert [item["actor"] for item in result["handoff_trace"]] == [
        "Line Production Agent",
        "Maintenance Engineering Agent",
        "Maintenance Engineering Agent",
        "Quality Process Agent",
        "Plant Manager Agent",
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
        "Line Production Agent",
        "Maintenance Engineering Agent",
        "Quality Process Agent",
        "Plant Manager Agent",
    }
    assert len(second_registration) == 4
    assert first_registration["Line Production Agent"].id == second_registration["Line Production Agent"].id


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
            customer_name="SMT Line 4",
            issue="Intermittent solder defects appear after material changeover.",
        ),
    )

    retrieval = next(
        activity for activity in result["activities"] if activity.action_type == "memory_retrieved"
    )

    assert retrieval.input_summary.startswith("Search query:")
    assert retrieval.output_summary == "Factory issue - SMT Line 4"

    stored_retrieval = session.get(Activity, retrieval.id)
    assert stored_retrieval is not None
    assert stored_retrieval.output_summary == "Factory issue - SMT Line 4"
