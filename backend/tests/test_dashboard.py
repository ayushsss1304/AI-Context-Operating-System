from datetime import datetime, timedelta

from app.models.activity import Activity
from app.models.agent import Agent
from app.models.approval import Approval
from app.models.memory import Memory
from app.models.task import Task
from app.models.workspace import Workspace
from app.api.routes.dashboard import build_demo_summary
from app.services.timeline_service import build_handoff_trace


def test_build_timeline_items_orders_handoffs_by_creation_time(session):
    workspace = Workspace(name="Timeline Test")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    support_agent = Agent(
        workspace_id=workspace.id,
        name="Support Agent",
        role="support",
        capabilities=[],
        permissions=[],
    )
    engineering_agent = Agent(
        workspace_id=workspace.id,
        name="Engineering Agent",
        role="engineering",
        capabilities=[],
        permissions=[],
    )
    session.add(support_agent)
    session.add(engineering_agent)
    session.commit()
    session.refresh(support_agent)
    session.refresh(engineering_agent)

    later = datetime.utcnow()
    earlier = later - timedelta(minutes=1)
    activities = [
        Activity(
            workspace_id=workspace.id,
            agent_id=engineering_agent.id,
            action_type="memory_retrieved",
            input_summary="Search query",
            output_summary="Customer issue memory",
            created_at=later,
        ),
        Activity(
            workspace_id=workspace.id,
            agent_id=support_agent.id,
            action_type="memory_created",
            input_summary="Customer issue",
            output_summary="Support summary",
            created_at=earlier,
        ),
    ]

    timeline_items = build_handoff_trace(
        activities,
        {
            str(support_agent.id): support_agent,
            str(engineering_agent.id): engineering_agent,
        },
    )

    assert [item["step"] for item in timeline_items] == ["1", "2"]
    assert timeline_items[0]["actor"] == "Support Agent"
    assert timeline_items[0]["label"] == "Stored shared memory"
    assert timeline_items[1]["actor"] == "Engineering Agent"
    assert timeline_items[1]["label"] == "Retrieved context"


def test_build_demo_summary_explains_active_task_state(session):
    workspace = Workspace(name="Summary Test")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    manager_agent = Agent(
        workspace_id=workspace.id,
        name="Manager Agent",
        role="manager",
        capabilities=[],
        permissions=[],
    )
    session.add(manager_agent)
    session.commit()
    session.refresh(manager_agent)

    task = Task(
        workspace_id=workspace.id,
        title="Investigate customer issue",
        status="waiting_for_approval",
        current_owner_agent_id=manager_agent.id,
    )
    memory = Memory(
        workspace_id=workspace.id,
        title="Customer issue",
        content="Settings disappear after refresh.",
        memory_type="customer_issue",
    )
    activity = Activity(
        workspace_id=workspace.id,
        task_id=task.id,
        agent_id=manager_agent.id,
        action_type="approval_requested",
        output_summary="Approve recommendation",
    )
    approval = Approval(
        workspace_id=workspace.id,
        task_id=task.id,
        title="Approval",
        content="Approve next step.",
    )

    summary = build_demo_summary(
        [manager_agent],
        [memory],
        [activity],
        [approval],
        task,
        [{"label": "Requested approval"}],
    )

    assert summary["ready"] is True
    assert summary["owner"] == "Manager Agent"
    assert summary["status"] == "waiting_for_approval"
    assert summary["current_step"] == "Requested approval"
    assert "1 shared memories" in summary["summary"]
