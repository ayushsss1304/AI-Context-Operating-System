from datetime import datetime, timedelta

from app.models.activity import Activity
from app.models.agent import Agent
from app.models.workspace import Workspace
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
