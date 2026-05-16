from sqlmodel import Session

from app.models.agent import Agent
from app.schemas.memory import MemoryCreate
from app.services.memory_service import MemoryService


PRODUCT_COMPANY_DEMO = {
    "workspace_name": "Panasonic Smart Factory Pilot",
    "workspace_description": "Factory issue-resolution pilot for workforce continuity.",
    "customer_name": "SMT Line 3",
    "issue": (
        "An SMT line starts showing intermittent solder defects after a material changeover. Operators see "
        "higher rework during the evening shift and need maintenance, quality, and plant management to align "
        "on next action."
    ),
}


PRODUCT_COMPANY_MEMORY_SEEDS = [
    {
        "title": "Prior incident - SMT solder bridge after paste lot change",
        "content": (
            "In March 2026, SMT Line 2 saw a short spike in solder bridging after a solder paste lot change and "
            "evening-shift feeder setup variation. Maintenance confirmed the reflow oven profile was inside "
            "control limits, while quality contained the lot and added first-hour inspection after changeover."
        ),
        "memory_type": "prior_incident",
        "tags": ["panasonic", "smt", "solder", "material-changeover", "prior-incident"],
        "importance_score": 0.86,
    },
    {
        "title": "Maintenance playbook - SMT changeover solder-defect triage",
        "content": (
            "For solder defects after SMT material changeover, maintenance should compare paste lot, stencil "
            "cleaning interval, feeder setup, nozzle condition, placement offsets, reflow profile history, and "
            "first-pass yield by hour. The handoff note should separate confirmed facts from suspected causes."
        ),
        "memory_type": "maintenance_playbook",
        "tags": ["maintenance", "smt", "changeover", "triage", "reflow"],
        "importance_score": 0.78,
    },
    {
        "title": "Quality policy - temporary containment for SMT solder defects",
        "content": (
            "When a solder-defect trend appears after material changeover, quality may request temporary "
            "containment if rework rises above the line baseline for two consecutive inspection windows. Plant "
            "management approval is required before changing inspection scope, holding WIP, or pausing the line."
        ),
        "memory_type": "quality_policy",
        "tags": ["quality", "containment", "inspection", "approval", "smt"],
        "importance_score": 0.82,
    },
]


def product_company_demo_defaults() -> dict[str, str]:
    return PRODUCT_COMPANY_DEMO.copy()


def seed_product_company_memories(
    session: Session,
    workspace_id,
    agents_by_name: dict[str, Agent],
    memory_service: MemoryService | None = None,
) -> list:
    memory_client = memory_service or MemoryService()
    engineering_agent = agents_by_name.get("Maintenance Engineering Agent")
    created_memories = []

    for seed in PRODUCT_COMPANY_MEMORY_SEEDS:
        memory = memory_client.create(
            session,
            MemoryCreate(
                workspace_id=workspace_id,
                created_by_agent_id=engineering_agent.id if engineering_agent else None,
                title=seed["title"],
                content=seed["content"],
                memory_type=seed["memory_type"],
                tags=seed["tags"],
                source="factory-demo-seed",
                importance_score=seed["importance_score"],
            ),
        )
        created_memories.append(memory)

    return created_memories
