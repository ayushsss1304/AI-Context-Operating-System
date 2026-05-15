from sqlmodel import SQLModel


class HandoffTraceItem(SQLModel):
    step: str
    label: str
    actor: str
    status: str
    input: str
    output: str
