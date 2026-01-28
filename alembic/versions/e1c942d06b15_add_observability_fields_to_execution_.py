"""Add observability fields to execution logs

Revision ID: e1c942d06b15
Revises: ba92e300a578
Create Date: 2026-01-23 19:28:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1c942d06b15"
down_revision: Union[str, Sequence[str], None] = "ba92e300a578"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "execution_logs",
        sa.Column("trace_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "execution_logs",
        sa.Column("payload_snapshot", sa.JSON(), nullable=True),
    )
    op.add_column(
        "execution_logs",
        sa.Column("action_duration_ms", sa.Numeric(12, 3), nullable=True),
    )

    op.execute(
        "UPDATE execution_logs SET trace_id = COALESCE(trace_id, 'legacy-trace')"
    )
    op.alter_column("execution_logs", "trace_id", nullable=False)

    op.create_index(
        "ix_execution_logs_workflow_status_created",
        "execution_logs",
        ["workflow_id", "status", "created_at"],
    )
    op.create_index(
        "ix_execution_logs_queued_to_dlq_created",
        "execution_logs",
        ["queued_to_dlq", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_execution_logs_queued_to_dlq_created", table_name="execution_logs")
    op.drop_index("ix_execution_logs_workflow_status_created", table_name="execution_logs")

    op.drop_column("execution_logs", "action_duration_ms")
    op.drop_column("execution_logs", "payload_snapshot")
    op.drop_column("execution_logs", "trace_id")
