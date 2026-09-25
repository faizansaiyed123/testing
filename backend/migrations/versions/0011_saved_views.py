"""Add reusable saved CRM views."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0011_saved_views"
down_revision = "0010_task_automation_key"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "saved_views",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "filters",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "columns",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_saved_views_owner_name",
        "saved_views",
        [
            "organization_id",
            "owner_user_id",
            "entity_type",
            sa.text("lower(name)"),
        ],
        unique=True,
    )
    op.create_index(
        "ix_saved_views_org_owner_entity",
        "saved_views",
        [
            "organization_id",
            "owner_user_id",
            "entity_type",
            "updated_at",
        ],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_saved_views_org_owner_entity",
        table_name="saved_views",
    )
    op.drop_index(
        "uq_saved_views_owner_name",
        table_name="saved_views",
    )
    op.drop_table("saved_views")
