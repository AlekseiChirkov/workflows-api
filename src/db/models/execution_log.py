import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    Numeric,
    ForeignKey,
    JSON,
    UniqueConstraint,
    Index,
    Integer,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from src.db.base import Base

class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    __table_args__ = (
        UniqueConstraint("event_id", "workflow_id", name="uq_execution_logs_event_workflow"),
        Index("ix_execution_logs_workflow_created", "workflow_id", "created_at"),
        Index("ix_execution_logs_workflow_status_created", "workflow_id", "status", "created_at"),
        Index("ix_execution_logs_queued_to_dlq_created", "queued_to_dlq", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id"),
        nullable=False,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    payload_snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    retryable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duration: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    action_duration_ms: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc)
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )
    queued_to_dlq: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=expression.false(),
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
