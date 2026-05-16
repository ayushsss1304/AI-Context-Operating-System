from app.api.routes.workflows import demo_bootstrap
from app.schemas.workflow import DemoBootstrapRequest
from app.services import workflow_service
from app.services.system_status_service import build_system_status


class FakeLLMService:
    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if "Line Production Agent" in system_prompt:
            return "Operators report intermittent solder defects after material changeover."
        if "Maintenance Engineering Agent" in system_prompt:
            return "Maintenance should inspect material changeover records and solder profile history."
        if "Quality Process Agent" in system_prompt:
            return "Quality should treat this as a rework and defect-risk issue."
        return fallback


def test_system_status_starts_needing_demo_data(session):
    status = build_system_status(session)

    assert status["status"] == "needs_demo_data"
    assert status["counts"]["workspaces"] == 0
    assert status["modules"][0]["name"] == "Workspace"
    assert status["modules"][0]["ready"] is False


def test_system_status_is_ready_after_demo_bootstrap(session, monkeypatch):
    monkeypatch.setattr(workflow_service, "LLMService", FakeLLMService)

    demo_bootstrap(
        DemoBootstrapRequest(
            workspace_name="Status Demo",
            customer_name="SMT Line 3",
            issue="Intermittent solder defects appear after material changeover.",
        ),
        session,
    )
    status = build_system_status(session)

    assert status["status"] == "ready"
    assert status["counts"]["workspaces"] == 1
    assert status["counts"]["agents"] == 4
    assert status["counts"]["memories"] == 6
    assert status["counts"]["activities"] == 5
    assert status["counts"]["pending_approvals"] == 1
    assert all(module["ready"] for module in status["modules"][:7])
