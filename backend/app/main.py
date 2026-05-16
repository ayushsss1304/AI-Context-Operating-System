from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import activities, agents, approvals, dashboard, memories, system, tasks, workflows, workspaces
from app.core.config import get_settings
from app.core.database import create_db_and_tables

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_run_migrations:
        run_migrations()
    if settings.auto_create_tables:
        create_db_and_tables()


def run_migrations() -> None:
    root_config = Path("alembic.ini")
    backend_config = Path(__file__).resolve().parents[1] / "alembic.ini"
    config_path = root_config if root_config.exists() else backend_config
    command.upgrade(Config(str(config_path)), "head")


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
app.include_router(system.router)
app.include_router(dashboard.router)
