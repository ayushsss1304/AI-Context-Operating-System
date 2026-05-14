from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from app.models.activity import Activity
from app.models.agent import Agent
from app.models.approval import Approval
from app.models.memory import Memory
from app.models.task import Task
from app.schemas.workflow import CustomerIssueDemoRequest


DEMO_AGENTS = [
    {
        "name": "Support Agent",
        "role": "support",
        "description": "Understands customer issues and creates clear summaries.",
        "capabilities": ["issue_summary", "memory_write"],
        "permissions": ["create_memory", "create_activity"],
    },
    {
        "name": "Engineering Agent",
        "role": "engineering",
        "description": "Reviews technical context and identifies likely causes.",
        "capabilities": ["memory_search", "technical_analysis"],
        "permissions": ["read_memory", "create_memory", "create_activity"],
    },
    {
        "name": "Product Agent",
        "role": "product",
        "description": "Converts technical and customer context into product impact.",
        "capabilities": ["impact_summary", "recommendation"],
        "permissions": ["read_memory", "create_memory", "create_activity"],
    },
    {
        "name": "Manager Agent",
        "role": "manager",
        "description": "Reviews outputs and requests human approval.",
        "capabilities": ["approval_request", "oversight"],
        "permissions": ["create_approval", "create_activity"],
    },
]


def ensure_demo_agents(session: Session, workspace_id: UUID) -> dict[str, Agent]:
    existing = session.exec(select(Agent).where(Agent.workspace_id == workspace_id)).all()
    agents_by_name = {agent.name: agent for agent in existing}

    for agent_data in DEMO_AGENTS:
        if agent_data["name"] not in agents_by_name:
            agent = Agent(workspace_id=workspace_id, **agent_data)
            session.add(agent)
            session.commit()
            session.refresh(agent)
            agents_by_name[agent.name] = agent

    return agents_by_name


def run_customer_issue_demo(session: Session, payload: CustomerIssueDemoRequest) -> dict:
    agents = ensure_demo_agents(session, payload.workspace_id)
    support_agent = agents["Support Agent"]
    engineering_agent = agents["Engineering Agent"]
    product_agent = agents["Product Agent"]
    manager_agent = agents["Manager Agent"]

    task = Task(
        workspace_id=payload.workspace_id,
        title=f"Investigate issue from {payload.customer_name}",
        description=payload.issue,
        status="in_progress",
        current_owner_agent_id=support_agent.id,
        priority="high",
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    support_summary = f"{payload.customer_name} reported: {payload.issue}"
    support_memory = Memory(
        workspace_id=payload.workspace_id,
        created_by_agent_id=support_agent.id,
        title=f"Customer issue - {payload.customer_name}",
        content=support_summary,
        memory_type="customer_issue",
        tags=["customer_issue", "support", payload.customer_name.lower().replace(" ", "-")],
        source="customer-issue-demo",
        importance_score=0.8,
    )
    session.add(support_memory)
    session.commit()
    session.refresh(support_memory)

    activities = [
        Activity(
            workspace_id=payload.workspace_id,
            task_id=task.id,
            agent_id=support_agent.id,
            action_type="memory_created",
            input_summary=payload.issue,
            output_summary=support_summary,
            full_output=support_summary,
        )
    ]

    engineering_note = (
        "Engineering reviewed the customer issue memory and should inspect recent changes, "
        "logs, and related error reports before proposing a fix."
    )
    engineering_memory = Memory(
        workspace_id=payload.workspace_id,
        created_by_agent_id=engineering_agent.id,
        title="Technical investigation note",
        content=engineering_note,
        memory_type="technical_note",
        tags=["engineering", "investigation"],
        source="customer-issue-demo",
        importance_score=0.7,
    )
    session.add(engineering_memory)
    session.commit()
    session.refresh(engineering_memory)

    activities.extend(
        [
            Activity(
                workspace_id=payload.workspace_id,
                task_id=task.id,
                agent_id=engineering_agent.id,
                action_type="memory_retrieved",
                input_summary="Retrieved support memory for technical context.",
                output_summary=support_memory.title,
                full_output=support_memory.content,
            ),
            Activity(
                workspace_id=payload.workspace_id,
                task_id=task.id,
                agent_id=engineering_agent.id,
                action_type="analysis_generated",
                input_summary=support_memory.content,
                output_summary=engineering_note,
                full_output=engineering_note,
            ),
        ]
    )

    product_summary = (
        "Product impact: this issue may affect customer trust and should be tracked as a "
        "workflow-continuity case until engineering confirms the root cause."
    )
    product_memory = Memory(
        workspace_id=payload.workspace_id,
        created_by_agent_id=product_agent.id,
        title="Product impact summary",
        content=product_summary,
        memory_type="product_note",
        tags=["product", "impact"],
        source="customer-issue-demo",
        importance_score=0.7,
    )
    session.add(product_memory)
    session.commit()
    session.refresh(product_memory)

    activities.append(
        Activity(
            workspace_id=payload.workspace_id,
            task_id=task.id,
            agent_id=product_agent.id,
            action_type="analysis_generated",
            input_summary=engineering_note,
            output_summary=product_summary,
            full_output=product_summary,
        )
    )

    approval = Approval(
        workspace_id=payload.workspace_id,
        task_id=task.id,
        requested_by_agent_id=manager_agent.id,
        title="Approve customer issue recommendation",
        content=f"{support_summary}\n\n{engineering_note}\n\n{product_summary}",
    )
    session.add(approval)

    task.status = "waiting_for_approval"
    task.current_owner_agent_id = manager_agent.id
    task.updated_at = datetime.utcnow()
    session.add(task)

    activities.append(
        Activity(
            workspace_id=payload.workspace_id,
            task_id=task.id,
            agent_id=manager_agent.id,
            action_type="approval_requested",
            input_summary=product_summary,
            output_summary=approval.title,
            full_output=approval.content,
        )
    )
    session.add_all(activities)
    session.commit()

    session.refresh(task)
    session.refresh(approval)
    for activity in activities:
        session.refresh(activity)

    return {
        "task": task,
        "memories": [support_memory, engineering_memory, product_memory],
        "activities": activities,
        "approval": approval,
    }
