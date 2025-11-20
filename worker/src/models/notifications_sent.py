import uuid

from sqlalchemy import Column, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.core.database import WorkerBase


class NotificationSent(WorkerBase):
    __tablename__ = "notifications_sent"
    __table_args__ = (
        UniqueConstraint(
            "subscriber_id",
            "post_id",
            name="ux_notifications_sent_subscriber_post",
        ),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscriber_id = Column(PG_UUID(as_uuid=True), nullable=False)
    post_id = Column(PG_UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
