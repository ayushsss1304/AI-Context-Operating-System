from app.models.activity import Activity
from app.models.agent import Agent


ACTION_LABELS = {
    "memory_created": "Stored shared memory",
    "memory_retrieved": "Retrieved context",
    "analysis_generated": "Generated analysis",
    "approval_requested": "Requested approval",
    "approval_reviewed": "Human review completed",
    "task_continued": "Continued task",
}


def build_handoff_trace(
    activities: list[Activity],
    agents_by_id: dict[str, Agent],
) -> list[dict[str, str]]:
    ordered_activities = sorted(activities, key=lambda activity: activity.created_at)
    trace_items = []

    for index, activity in enumerate(ordered_activities, start=1):
        agent = agents_by_id.get(str(activity.agent_id)) if activity.agent_id else None
        trace_items.append(
            {
                "step": str(index),
                "label": ACTION_LABELS.get(activity.action_type, activity.action_type.replace("_", " ").title()),
                "actor": agent.name if agent else "Human Manager",
                "status": activity.status,
                "input": activity.input_summary or "",
                "output": activity.output_summary or activity.full_output or activity.status,
            }
        )

    return trace_items
