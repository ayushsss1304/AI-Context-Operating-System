from app.api.routes.tasks import continue_task
from app.models.workspace import Workspace
from app.schemas.task import TaskContinuationRequest
from app.schemas.workflow import CustomerIssueDemoRequest
from app.services import task_continuation_service, workflow_service


class FakeWorkflowLLMService:
    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if "Support Agent" in system_prompt:
            return "Customer reports settings disappear after refresh."
        if "Engineering Agent" in system_prompt:
            return "Engineering should inspect persistence and settings APIs."
        if "Product Agent" in system_prompt:
            return "Product should treat this as a high-trust workflow continuity issue."
        return fallback


class FakeContinuationLLMService:
    def generate(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        return "Engineering resumed the task from shared context. It will inspect persistence, API writes, and reload behavior. The next update should confirm the root cause."


def test_continue_task_from_context_writes_memory_and_updates_owner(session, monkeypatch):
    monkeypatch.setattr(workflow_service, "LLMService", FakeWorkflowLLMService)
    monkeypatch.setattr(task_continuation_service, "LLMService", FakeContinuationLLMService)
    workspace = Workspace(name="Continuation Test", description="Resume task")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    result = workflow_service.run_customer_issue_demo(
        session,
        CustomerIssueDemoRequest(
            workspace_id=workspace.id,
            customer_name="ContinuationCo",
            issue="Saved settings disappear after page refresh.",
        ),
    )
    engineering_agent = result["task"].current_owner_agent_id
    for agent in result["handoff_trace"]:
        assert agent["actor"]

    registered_agents = workflow_service.ensure_demo_agents(session, workspace.id)
    engineering_agent = registered_agents["Engineering Agent"]

    continuation = continue_task(
        result["task"].id,
        TaskContinuationRequest(
            agent_id=engineering_agent.id,
            instruction="Resume engineering investigation and identify next technical checks.",
        ),
        session,
    )

    assert continuation["task"].status == "in_progress"
    assert continuation["task"].current_owner_agent_id == engineering_agent.id
    assert continuation["memory"].memory_type == "continuation_note"
    assert continuation["activity"].action_type == "task_continued"
    assert continuation["context_packet"]["current_owner"].name == "Engineering Agent"
    assert continuation["context_packet"]["handoff_trace"][-1]["label"] == "Continued task"
