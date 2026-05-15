"""initial schema

Revision ID: 20260515_0001
Revises:
Create Date: 2026-05-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "20260515_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspace",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=160), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workspace_name"), "workspace", ["name"], unique=False)

    op.create_table(
        "agent",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("capabilities", sa.JSON(), nullable=True),
        sa.Column("permissions", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_name"), "agent", ["name"], unique=False)
    op.create_index(op.f("ix_agent_workspace_id"), "agent", ["workspace_id"], unique=False)

    op.create_table(
        "task",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=180), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column("current_owner_agent_id", sa.Uuid(), nullable=True),
        sa.Column("priority", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["current_owner_agent_id"], ["agent.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_current_owner_agent_id"), "task", ["current_owner_agent_id"], unique=False)
    op.create_index(op.f("ix_task_status"), "task", ["status"], unique=False)
    op.create_index(op.f("ix_task_title"), "task", ["title"], unique=False)
    op.create_index(op.f("ix_task_workspace_id"), "task", ["workspace_id"], unique=False)

    op.create_table(
        "memory",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_agent_id", sa.Uuid(), nullable=True),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=180), nullable=False),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("memory_type", sqlmodel.sql.sqltypes.AutoString(length=80), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("source", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("importance_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_agent_id"], ["agent.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_memory_created_by_agent_id"), "memory", ["created_by_agent_id"], unique=False)
    op.create_index(op.f("ix_memory_memory_type"), "memory", ["memory_type"], unique=False)
    op.create_index(op.f("ix_memory_title"), "memory", ["title"], unique=False)
    op.create_index(op.f("ix_memory_workspace_id"), "memory", ["workspace_id"], unique=False)

    op.create_table(
        "approval",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("requested_by_agent_id", sa.Uuid(), nullable=True),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=180), nullable=False),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column("reviewed_by", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["requested_by_agent_id"], ["agent.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_approval_requested_by_agent_id"), "approval", ["requested_by_agent_id"], unique=False)
    op.create_index(op.f("ix_approval_status"), "approval", ["status"], unique=False)
    op.create_index(op.f("ix_approval_task_id"), "approval", ["task_id"], unique=False)
    op.create_index(op.f("ix_approval_workspace_id"), "approval", ["workspace_id"], unique=False)

    op.create_table(
        "activity",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=True),
        sa.Column("agent_id", sa.Uuid(), nullable=True),
        sa.Column("action_type", sqlmodel.sql.sqltypes.AutoString(length=80), nullable=False),
        sa.Column("input_summary", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("output_summary", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("full_output", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agent.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspace.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activity_action_type"), "activity", ["action_type"], unique=False)
    op.create_index(op.f("ix_activity_agent_id"), "activity", ["agent_id"], unique=False)
    op.create_index(op.f("ix_activity_status"), "activity", ["status"], unique=False)
    op.create_index(op.f("ix_activity_task_id"), "activity", ["task_id"], unique=False)
    op.create_index(op.f("ix_activity_workspace_id"), "activity", ["workspace_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_activity_workspace_id"), table_name="activity")
    op.drop_index(op.f("ix_activity_task_id"), table_name="activity")
    op.drop_index(op.f("ix_activity_status"), table_name="activity")
    op.drop_index(op.f("ix_activity_agent_id"), table_name="activity")
    op.drop_index(op.f("ix_activity_action_type"), table_name="activity")
    op.drop_table("activity")

    op.drop_index(op.f("ix_approval_workspace_id"), table_name="approval")
    op.drop_index(op.f("ix_approval_task_id"), table_name="approval")
    op.drop_index(op.f("ix_approval_status"), table_name="approval")
    op.drop_index(op.f("ix_approval_requested_by_agent_id"), table_name="approval")
    op.drop_table("approval")

    op.drop_index(op.f("ix_memory_workspace_id"), table_name="memory")
    op.drop_index(op.f("ix_memory_title"), table_name="memory")
    op.drop_index(op.f("ix_memory_memory_type"), table_name="memory")
    op.drop_index(op.f("ix_memory_created_by_agent_id"), table_name="memory")
    op.drop_table("memory")

    op.drop_index(op.f("ix_task_workspace_id"), table_name="task")
    op.drop_index(op.f("ix_task_title"), table_name="task")
    op.drop_index(op.f("ix_task_status"), table_name="task")
    op.drop_index(op.f("ix_task_current_owner_agent_id"), table_name="task")
    op.drop_table("task")

    op.drop_index(op.f("ix_agent_workspace_id"), table_name="agent")
    op.drop_index(op.f("ix_agent_name"), table_name="agent")
    op.drop_table("agent")

    op.drop_index(op.f("ix_workspace_name"), table_name="workspace")
    op.drop_table("workspace")
