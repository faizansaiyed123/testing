"""Add idempotency key for automated tasks."""

import sqlalchemy as sa
from alembic import op

revision = "0010_task_automation_key"
down_revision = "0009_opportunity_stage_age"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("automation_key", sa.String(length=200), nullable=True),
    )
    op.create_index(
        "uq_tasks_org_automation_key",
        "tasks",
        ["organization_id", "automation_key"],
        unique=True,
        postgresql_where=sa.text("automation_key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_tasks_org_automation_key", table_name="tasks")
    op.drop_column("tasks", "automation_key")
