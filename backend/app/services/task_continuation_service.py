from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.models.activity import Activity
from app.models.agent import Agent
from app.models.task import Task
from app.schemas.memory import MemoryCreate
from app.services.context_packet_service import build_task_context_packet
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService


def continue_task_from_context(
    session: Session,
    task_id: UUID,
    agent_id: UUID,
    instruction: str,
    llm: LLMService | None = None,
    memory_service: MemoryService | None = None,
) -> dict:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    agent = session.get(Agent, agent_id)
    if not agent or agent.workspace_id != task.workspace_id:
        raise HTTPException(status_code=404, detail="Agent not found for task workspace")

    memory_client = memory_service or MemoryService()
    context_packet = build_task_context_packet(session, task.id, memory_client)
    continuation_note = _generate_continuation_note(
        agent,
        instruction,
        context_packet,
        llm or LLMService(),
    )

    memory = memory_client.create(
        session,
        MemoryCreate(
            workspace_id=task.workspace_id,
            created_by_agent_id=agent.id,
            title=f"Continuation note - {agent.name}",
            content=continuation_note,
            memory_type="continuation_note",
            tags=["continuation", agent.role, str(task.id)],
            source="task-continuation",
            importance_score=0.75,
        ),
    )

    task.status = "in_progress"
    task.current_owner_agent_id = agent.id
    task.updated_at = datetime.utcnow()
    session.add(task)

    activity = Activity(
        workspace_id=task.workspace_id,
        task_id=task.id,
        agent_id=agent.id,
        action_type="task_continued",
        input_summary=instruction,
        output_summary=continuation_note,
        full_output=continuation_note,
    )
    session.add(activity)
    session.commit()
    session.refresh(task)
    session.refresh(activity)

    return {
        "task": task,
        "memory": memory,
        "activity": activity,
        "context_packet": build_task_context_packet(session, task.id, memory_client),
    }


def _generate_continuation_note(
    agent: Agent,
    instruction: str,
    context_packet: dict,
    llm: LLMService,
) -> str:
    memories = "\n".join(
        f"- {memory.title}: {memory.content}" for memory in context_packet["relevant_memories"][:5]
    )
    trace = "\n".join(
        f"- {item['step']}. {item['actor']} {item['label']}: {item['output']}"
        for item in context_packet["handoff_trace"]
    )
    fallback = (
        f"{agent.name} resumed the task using the available context. "
        f"Next action: {instruction}"
    )
    return llm.generate(
        system_prompt=(
            "You are an agent resuming work inside an AI Context Operating System. "
            "Use the provided task context, memories, and handoff trace to create a concise continuation note. "
            "Do not invent facts. Return 3 concise plain-text sentences with no markdown."
        ),
        user_prompt=(
            f"Agent: {agent.name} ({agent.role})\n"
            f"Instruction: {instruction}\n"
            f"Resume summary: {context_packet['resume_summary']}\n\n"
            f"Relevant memories:\n{memories}\n\n"
            f"Handoff trace:\n{trace}"
        ),
        fallback=fallback,
    )
