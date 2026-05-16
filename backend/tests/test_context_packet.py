from app.api.routes.tasks import get_task_context_packet
from app.models.workspace import Workspace
from app.schemas.workflow import CustomerIssueDemoRequest
from app.services import workflow_service


class FakeLLMService:
    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if "Line Production Agent" in system_prompt:
            return "Operators report intermittent solder defects after material changeover."
        if "Maintenance Engineering Agent" in system_prompt:
            return "Maintenance should inspect material changeover records and solder profile history."
        if "Quality Process Agent" in system_prompt:
            return "Quality should treat solder defects after material changeover as a rework and defect-risk issue."
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
            customer_name="SMT Line 3",
            issue="Intermittent solder defects appear after material changeover.",
        ),
    )

    packet = get_task_context_packet(result["task"].id, session)

    assert packet["task"].id == result["task"].id
    assert packet["current_owner"].name == "Plant Manager Agent"
    assert len(packet["relevant_memories"]) == 3
    assert len(packet["approvals"]) == 1
    assert len(packet["handoff_trace"]) == 5
    assert "waiting_for_approval" in packet["resume_summary"]
    assert "Plant Manager Agent" in packet["resume_summary"]
