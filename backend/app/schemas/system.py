from sqlmodel import SQLModel


class SystemModuleStatus(SQLModel):
    name: str
    ready: bool
    detail: str


class SystemStatus(SQLModel):
    status: str
    app: str
    env: str
    llm_provider: str
    llm_configured: bool
    counts: dict[str, int]
    modules: list[SystemModuleStatus]
