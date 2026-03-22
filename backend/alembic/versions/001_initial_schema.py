"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-22

"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inquiry_logs",
        sa.Column("inquiry_id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=True),
        sa.Column("channel", sa.String(100), nullable=True),
        sa.Column("locale", sa.String(20), nullable=True),
        sa.Column("inquiry_text_masked", sa.Text, nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("routing_reason", sa.Text, nullable=True),
        sa.Column("selected_agent", sa.String(100), nullable=True),
        sa.Column("answer", sa.Text, nullable=True),
        sa.Column("safety_flag", sa.Boolean, nullable=True),
        sa.Column("fallback_used", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("llm_call_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("error", sa.String(100), nullable=True),
        sa.Column("execution_trace", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_inquiry_logs_user_id", "inquiry_logs", ["user_id"])
    op.create_index("ix_inquiry_logs_category", "inquiry_logs", ["category"])
    op.create_index("ix_inquiry_logs_created_at", "inquiry_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_inquiry_logs_created_at", "inquiry_logs")
    op.drop_index("ix_inquiry_logs_category", "inquiry_logs")
    op.drop_index("ix_inquiry_logs_user_id", "inquiry_logs")
    op.drop_table("inquiry_logs")
