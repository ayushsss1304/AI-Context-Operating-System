from sqlalchemy import func
from sqlmodel import Session, select

from app.core.config import Settings, get_settings
from app.models.activity import Activity
from app.models.agent import Agent
from app.models.approval import Approval
from app.models.memory import Memory
from app.models.task import Task
from app.models.workspace import Workspace


def build_system_status(session: Session, settings: Settings | None = None) -> dict:
    active_settings = settings or get_settings()
    counts = {
        "workspaces": _count(session, Workspace),
        "agents": _count(session, Agent),
        "memories": _count(session, Memory),
        "tasks": _count(session, Task),
        "activities": _count(session, Activity),
        "approvals": _count(session, Approval),
        "pending_approvals": _count_pending_approvals(session),
    }
    llm_configured = _is_llm_configured(active_settings)
    modules = [
        _module("Workspace", counts["workspaces"] > 0, f"{counts['workspaces']} workspaces"),
        _module("Agent Registry", counts["agents"] >= 4, f"{counts['agents']} registered agents"),
        _module("Shared Memory Store", counts["memories"] > 0, f"{counts['memories']} memories"),
        _module("Task Workflow System", counts["tasks"] > 0, f"{counts['tasks']} tasks"),
        _module("Activity Timeline", counts["activities"] > 0, f"{counts['activities']} events"),
        _module("Human Approval Layer", counts["approvals"] > 0, f"{counts['approvals']} approvals"),
        _module("Workflow Continuity", counts["activities"] >= 5 and counts["memories"] >= 3, "handoff trace and context packets available"),
        _module("LLM Provider", llm_configured, f"{active_settings.default_llm_provider} configured"),
    ]
    ready = all(module["ready"] for module in modules[:7])

    return {
        "status": "ready" if ready else "needs_demo_data",
        "app": active_settings.app_name,
        "env": active_settings.app_env,
        "llm_provider": active_settings.default_llm_provider,
        "llm_configured": llm_configured,
        "counts": counts,
        "modules": modules,
    }


def _count(session: Session, model: type) -> int:
    return session.exec(select(func.count(model.id))).one()


def _count_pending_approvals(session: Session) -> int:
    return session.exec(select(func.count(Approval.id)).where(Approval.status == "pending")).one()


def _module(name: str, ready: bool, detail: str) -> dict[str, str | bool]:
    return {
        "name": name,
        "ready": ready,
        "detail": detail,
    }


def _is_llm_configured(settings: Settings) -> bool:
    provider = settings.default_llm_provider.lower()
    if provider == "groq":
        return bool(settings.groq_api_key)
    if provider == "openrouter":
        return bool(settings.openrouter_api_key)
    if provider == "together":
        return bool(settings.together_api_key)
    return False
