from app.api.routes.workflows import demo_bootstrap
from app.schemas.workflow import DemoBootstrapRequest
from app.services import workflow_service


class FakeLLMService:
    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if "Line Production Agent" in system_prompt:
            return "Operators report intermittent solder defects after material changeover."
        if "Maintenance Engineering Agent" in system_prompt:
            return "Maintenance should inspect material changeover records and solder profile history."
        if "Quality Process Agent" in system_prompt:
            return "Quality should treat this as a rework and defect-risk issue."
        return fallback


def test_demo_bootstrap_creates_workspace_and_runs_full_demo(session, monkeypatch):
    monkeypatch.setattr(workflow_service, "LLMService", FakeLLMService)

    result = demo_bootstrap(
        DemoBootstrapRequest(
            workspace_name="Bootstrap Demo",
            workspace_description="One call MVP setup",
            customer_name="SMT Line 3",
            issue="Intermittent solder defects appear after material changeover.",
        ),
        session,
    )

    assert result["overview"]["workspace"].name == "Bootstrap Demo"
    assert len(result["overview"]["agents"]) == 4
    assert len(result["overview"]["tasks"]) == 1
    assert len(result["overview"]["memories"]) == 6
    assert len(result["overview"]["approvals"]) == 1
    assert result["workflow"]["task"].status == "waiting_for_approval"
    assert len(result["workflow"]["handoff_trace"]) == 5
    assert result["overview"]["handoff_trace"][-1]["actor"] == "Plant Manager Agent"
    assert any(
        memory.title == "Prior incident - SMT solder bridge after paste lot change"
        for memory in result["overview"]["memories"]
    )
