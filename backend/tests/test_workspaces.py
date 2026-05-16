from app.api.routes.workspaces import create_workspace, get_workspace_overview
from app.models.agent import Agent
from app.models.workspace import Workspace
from app.schemas.workflow import CustomerIssueDemoRequest
from app.schemas.workspace import WorkspaceCreate
from app.services import workflow_service
from sqlmodel import select


class FakeLLMService:
    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if "Line Production Agent" in system_prompt:
            return "Operators report intermittent solder defects after material changeover."
        if "Maintenance Engineering Agent" in system_prompt:
            return "Maintenance should inspect material changeover records and solder profile history."
        if "Quality Process Agent" in system_prompt:
            return "Quality should treat this as a rework and defect-risk issue."
        return fallback


def test_create_workspace_registers_demo_agents(session):
    workspace = create_workspace(
        WorkspaceCreate(name="Overview Workspace", description="Workspace state"),
        session,
    )

    agents = session.exec(select(Agent).where(Agent.workspace_id == workspace.id)).all()

    assert {agent.name for agent in agents} == {
        "Line Production Agent",
        "Maintenance Engineering Agent",
        "Quality Process Agent",
        "Plant Manager Agent",
    }


def test_workspace_overview_returns_latest_context_state(session, monkeypatch):
    monkeypatch.setattr(workflow_service, "LLMService", FakeLLMService)
    workspace = Workspace(name="Overview Test", description="Full state")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    workflow_service.run_customer_issue_demo(
        session,
        CustomerIssueDemoRequest(
            workspace_id=workspace.id,
            customer_name="SMT Line 3",
            issue="Intermittent solder defects appear after material changeover.",
        ),
    )

    overview = get_workspace_overview(workspace.id, session)

    assert overview["workspace"].id == workspace.id
    assert len(overview["agents"]) == 4
    assert len(overview["tasks"]) == 1
    assert len(overview["memories"]) == 3
    assert len(overview["approvals"]) == 1
    assert overview["active_task"].status == "waiting_for_approval"
    assert [item["actor"] for item in overview["handoff_trace"]] == [
        "Line Production Agent",
        "Maintenance Engineering Agent",
        "Maintenance Engineering Agent",
        "Quality Process Agent",
        "Plant Manager Agent",
    ]
