from fastapi import FastAPI

from app.api.routes import activities, agents, approvals, memories, tasks, workflows, workspaces
from app.core.config import get_settings
from app.core.database import create_db_and_tables

settings = get_settings()

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


app.include_router(workspaces.router)
app.include_router(agents.router)
app.include_router(memories.router)
app.include_router(tasks.router)
app.include_router(activities.router)
app.include_router(approvals.router)
app.include_router(workflows.router)
