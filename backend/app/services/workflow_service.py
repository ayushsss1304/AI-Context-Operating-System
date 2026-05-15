from datetime import datetime
from typing import TypedDict
from uuid import UUID

from langgraph.graph import END, StateGraph
from sqlmodel import Session, select

from app.models.activity import Activity
from app.models.agent import Agent
from app.models.approval import Approval
from app.models.memory import Memory
from app.models.task import Task
from app.schemas.memory import MemoryCreate, MemorySearchRequest
from app.schemas.workflow import CustomerIssueDemoRequest
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.timeline_service import build_handoff_trace


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


class CustomerIssueWorkflowState(TypedDict, total=False):
    session: Session
    payload: CustomerIssueDemoRequest
    llm: LLMService
    memory_service: MemoryService
    agents: dict[str, Agent]
    task: Task
    memories: list[Memory]
    activities: list[Activity]
    approval: Approval
    support_summary: str
    engineering_note: str
    product_summary: str
    retrieved_memories: list[Memory]


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


def create_task_node(state: CustomerIssueWorkflowState) -> CustomerIssueWorkflowState:
    session = state["session"]
    payload = state["payload"]
    agents = ensure_demo_agents(session, payload.workspace_id)
    support_agent = agents["Support Agent"]

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

    return {
        **state,
        "agents": agents,
        "task": task,
        "memories": [],
        "activities": [],
    }


def support_agent_node(state: CustomerIssueWorkflowState) -> CustomerIssueWorkflowState:
    session = state["session"]
    payload = state["payload"]
    task = state["task"]
    support_agent = state["agents"]["Support Agent"]

    fallback = f"{payload.customer_name} reported: {payload.issue}"
    support_summary = state["llm"].generate(
        system_prompt=(
            "You are the Support Agent in an AI coordination system. "
            "Summarize customer issues clearly and preserve concrete details. "
            "Return 2 concise plain-text sentences. Do not use markdown, headings, bullets, or labels."
        ),
        user_prompt=f"Customer: {payload.customer_name}\nIssue: {payload.issue}",
        fallback=fallback,
    )
    memory = state["memory_service"].create(
        session,
        MemoryCreate(
            workspace_id=payload.workspace_id,
            created_by_agent_id=support_agent.id,
            title=f"Customer issue - {payload.customer_name}",
            content=support_summary,
            memory_type="customer_issue",
            tags=["customer_issue", "support", payload.customer_name.lower().replace(" ", "-")],
            source="customer-issue-demo",
            importance_score=0.8,
        ),
    )

    activity = Activity(
        workspace_id=payload.workspace_id,
        task_id=task.id,
        agent_id=support_agent.id,
        action_type="memory_created",
        input_summary=payload.issue,
        output_summary=support_summary,
        full_output=support_summary,
    )

    return {
        **state,
        "support_summary": support_summary,
        "memories": [*state["memories"], memory],
        "activities": [*state["activities"], activity],
    }


def engineering_agent_node(state: CustomerIssueWorkflowState) -> CustomerIssueWorkflowState:
    session = state["session"]
    payload = state["payload"]
    task = state["task"]
    engineering_agent = state["agents"]["Engineering Agent"]
    retrieval_query = f"{payload.customer_name} {payload.issue}"
    retrieved_memories = state["memory_service"].search(
        session,
        MemorySearchRequest(
            workspace_id=payload.workspace_id,
            query=retrieval_query,
            limit=3,
        ),
    )
    support_memory = retrieved_memories[0] if retrieved_memories else state["memories"][0]

    fallback = (
        "Engineering reviewed the customer issue memory and should inspect recent changes, "
        "logs, and related error reports before proposing a fix."
    )
    engineering_note = state["llm"].generate(
        system_prompt=(
            "You are the Engineering Agent in an AI coordination system. "
            "Create a practical technical investigation note from the shared support memory. "
            "Mention likely areas to inspect, but do not pretend to know facts not provided. "
            "Return 3 concise plain-text sentences. Do not use markdown, headings, bullets, or labels."
        ),
        user_prompt=f"Support memory:\n{support_memory.content}",
        fallback=fallback,
    )
    memory = state["memory_service"].create(
        session,
        MemoryCreate(
            workspace_id=payload.workspace_id,
            created_by_agent_id=engineering_agent.id,
            title="Technical investigation note",
            content=engineering_note,
            memory_type="technical_note",
            tags=["engineering", "investigation"],
            source="customer-issue-demo",
            importance_score=0.7,
        ),
    )

    activities = [
        Activity(
            workspace_id=payload.workspace_id,
            task_id=task.id,
            agent_id=engineering_agent.id,
            action_type="memory_retrieved",
            input_summary=f"Search query: {retrieval_query}",
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

    return {
        **state,
        "engineering_note": engineering_note,
        "retrieved_memories": retrieved_memories,
        "memories": [*state["memories"], memory],
        "activities": [*state["activities"], *activities],
    }


def product_agent_node(state: CustomerIssueWorkflowState) -> CustomerIssueWorkflowState:
    session = state["session"]
    payload = state["payload"]
    task = state["task"]
    product_agent = state["agents"]["Product Agent"]
    engineering_note = state["engineering_note"]

    fallback = (
        "Product impact: this issue may affect customer trust and should be tracked as a "
        "workflow-continuity case until engineering confirms the root cause."
    )
    product_summary = state["llm"].generate(
        system_prompt=(
            "You are the Product Agent in an AI coordination system. "
            "Convert support and engineering context into a product impact summary. "
            "Focus on user impact, priority, and what a manager should approve next. "
            "Return 3 concise plain-text sentences. Do not use markdown, headings, bullets, or labels."
        ),
        user_prompt=(
            f"Support summary:\n{state['support_summary']}\n\n"
            f"Engineering note:\n{engineering_note}"
        ),
        fallback=fallback,
    )
    memory = state["memory_service"].create(
        session,
        MemoryCreate(
            workspace_id=payload.workspace_id,
            created_by_agent_id=product_agent.id,
            title="Product impact summary",
            content=product_summary,
            memory_type="product_note",
            tags=["product", "impact"],
            source="customer-issue-demo",
            importance_score=0.7,
        ),
    )

    activity = Activity(
        workspace_id=payload.workspace_id,
        task_id=task.id,
        agent_id=product_agent.id,
        action_type="analysis_generated",
        input_summary=engineering_note,
        output_summary=product_summary,
        full_output=product_summary,
    )

    return {
        **state,
        "product_summary": product_summary,
        "memories": [*state["memories"], memory],
        "activities": [*state["activities"], activity],
    }


def manager_agent_node(state: CustomerIssueWorkflowState) -> CustomerIssueWorkflowState:
    session = state["session"]
    payload = state["payload"]
    task = state["task"]
    manager_agent = state["agents"]["Manager Agent"]

    approval = Approval(
        workspace_id=payload.workspace_id,
        task_id=task.id,
        requested_by_agent_id=manager_agent.id,
        title="Approve customer issue recommendation",
        content=f"{state['support_summary']}\n\n{state['engineering_note']}\n\n{state['product_summary']}",
    )
    session.add(approval)

    task.status = "waiting_for_approval"
    task.current_owner_agent_id = manager_agent.id
    task.updated_at = datetime.utcnow()
    session.add(task)

    activity = Activity(
        workspace_id=payload.workspace_id,
        task_id=task.id,
        agent_id=manager_agent.id,
        action_type="approval_requested",
        input_summary=state["product_summary"],
        output_summary=approval.title,
        full_output=approval.content,
    )
    activities = [*state["activities"], activity]
    session.add_all(activities)
    session.commit()

    session.refresh(task)
    session.refresh(approval)
    for saved_activity in activities:
        session.refresh(saved_activity)

    return {
        **state,
        "task": task,
        "approval": approval,
        "activities": activities,
    }


def build_customer_issue_graph():
    graph = StateGraph(CustomerIssueWorkflowState)
    graph.add_node("create_task", create_task_node)
    graph.add_node("support_agent", support_agent_node)
    graph.add_node("engineering_agent", engineering_agent_node)
    graph.add_node("product_agent", product_agent_node)
    graph.add_node("manager_agent", manager_agent_node)

    graph.set_entry_point("create_task")
    graph.add_edge("create_task", "support_agent")
    graph.add_edge("support_agent", "engineering_agent")
    graph.add_edge("engineering_agent", "product_agent")
    graph.add_edge("product_agent", "manager_agent")
    graph.add_edge("manager_agent", END)
    return graph.compile()


def run_customer_issue_demo(session: Session, payload: CustomerIssueDemoRequest) -> dict:
    graph = build_customer_issue_graph()
    final_state = graph.invoke(
        {
            "session": session,
            "payload": payload,
            "llm": LLMService(),
            "memory_service": MemoryService(),
        }
    )

    return {
        "task": final_state["task"],
        "memories": final_state["memories"],
        "activities": final_state["activities"],
        "approval": final_state["approval"],
        "handoff_trace": build_handoff_trace(final_state["activities"], {
            str(agent.id): agent for agent in final_state["agents"].values()
        }),
    }
