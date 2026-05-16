from sqlmodel import Session

from app.models.agent import Agent
from app.schemas.memory import MemoryCreate
from app.services.memory_service import MemoryService


PRODUCT_COMPANY_DEMO = {
    "workspace_name": "Panasonic Smart TV Reliability Desk",
    "workspace_description": "Shared AI workspace for connected TV support, QA, firmware, product, and release decisions.",
    "customer_name": "Panasonic Support Escalation - Europe Smart TV Line",
    "issue": (
        "After firmware v4.18.2 shipped to Panasonic MX800 and MX950 Smart TV models in Germany and the UK, "
        "customers report Wi-Fi disconnects within 10 to 20 minutes of opening Netflix or YouTube. Support has "
        "42 tickets in 36 hours, mostly from dual-band home routers. Rebooting the TV temporarily restores the "
        "connection, but the issue returns after streaming resumes."
    ),
}


PRODUCT_COMPANY_MEMORY_SEEDS = [
    {
        "title": "Prior incident - MX700 Wi-Fi reconnect regression",
        "content": (
            "In Q4 2025, MX700 units on firmware v3.9.7 showed intermittent Wi-Fi reconnect failures after long "
            "streaming sessions. Engineering traced the issue to a power-save state transition in the wireless "
            "driver after DHCP lease renewal. The fix was shipped in v3.9.9 after QA reproduced it on FritzBox "
            "and BT Smart Hub routers."
        ),
        "memory_type": "prior_incident",
        "tags": ["panasonic", "smart-tv", "wifi", "firmware", "mx700", "dhcp"],
        "importance_score": 0.86,
    },
    {
        "title": "QA playbook - streaming connectivity regression",
        "content": (
            "For Smart TV connectivity regressions, QA should test Netflix, YouTube, and Prime Video on 2.4 GHz "
            "and 5 GHz networks, capture wireless driver logs, check DHCP renewals, and compare cold boot versus "
            "resume-from-standby behavior. Router coverage should include FritzBox 7590, BT Smart Hub 2, TP-Link "
            "Archer AX series, and ISP-provided dual-band routers."
        ),
        "memory_type": "qa_playbook",
        "tags": ["qa", "streaming", "wifi", "router-matrix", "reproduction"],
        "importance_score": 0.78,
    },
    {
        "title": "Release policy - connected TV hotfix threshold",
        "content": (
            "A connected TV firmware issue qualifies for hotfix review when it affects core streaming behavior, "
            "appears within 72 hours of release, and has more than 25 confirmed support tickets across at least "
            "two regions. Product, firmware, QA, and release management must approve rollback or staged hotfix "
            "before customer advisory publication."
        ),
        "memory_type": "release_policy",
        "tags": ["release", "hotfix", "support-threshold", "customer-advisory"],
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
    engineering_agent = agents_by_name.get("Engineering Agent")
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
                source="product-company-demo-seed",
                importance_score=seed["importance_score"],
            ),
        )
        created_memories.append(memory)

    return created_memories
