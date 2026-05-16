from app.api.routes.workflows import demo_bootstrap
from app.schemas.workflow import DemoBootstrapRequest
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


def test_demo_bootstrap_creates_workspace_and_runs_full_demo(session, monkeypatch):
    monkeypatch.setattr(workflow_service, "LLMService", FakeLLMService)

    result = demo_bootstrap(
        DemoBootstrapRequest(
            workspace_name="Bootstrap Demo",
            workspace_description="One call MVP setup",
            customer_name="BootstrapCo",
            issue="Settings disappear after browser refresh.",
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
    assert result["overview"]["handoff_trace"][-1]["actor"] == "Manager Agent"
    assert any(
        memory.title == "Prior incident - MX700 Wi-Fi reconnect regression"
        for memory in result["overview"]["memories"]
    )
