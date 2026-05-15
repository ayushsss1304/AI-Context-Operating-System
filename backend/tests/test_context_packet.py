from app.api.routes.tasks import get_task_context_packet
from app.models.workspace import Workspace
from app.schemas.workflow import CustomerIssueDemoRequest
from app.services import workflow_service


class FakeLLMService:
    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if "Support Agent" in system_prompt:
            return "Customer reports settings disappear after refresh."
        if "Engineering Agent" in system_prompt:
            return "Engineering should inspect persistence and settings APIs."
        if "Product Agent" in system_prompt:
            return "Product should treat this as a high-trust workflow continuity issue."
        return fallback


def test_task_context_packet_returns_resume_ready_state(session, monkeypatch):
    monkeypatch.setattr(workflow_service, "LLMService", FakeLLMService)
    workspace = Workspace(name="Context Packet Test", description="Resume task")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    result = workflow_service.run_customer_issue_demo(
        session,
        CustomerIssueDemoRequest(
            workspace_id=workspace.id,
            customer_name="PacketCo",
            issue="Saved settings disappear after page refresh.",
        ),
    )

    packet = get_task_context_packet(result["task"].id, session)

    assert packet["task"].id == result["task"].id
    assert packet["current_owner"].name == "Manager Agent"
    assert len(packet["relevant_memories"]) == 3
    assert len(packet["approvals"]) == 1
    assert len(packet["handoff_trace"]) == 5
    assert "waiting_for_approval" in packet["resume_summary"]
    assert "Manager Agent" in packet["resume_summary"]
