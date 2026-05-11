"""add agent_version column to inquiry_logs

Revision ID: 003
Revises: 002
Create Date: 2026-05-11

"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "inquiry_logs",
        sa.Column("agent_version", sa.String(10), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("inquiry_logs", "agent_version")
