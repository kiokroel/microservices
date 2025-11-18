import uuid

from sqlalchemy import Column, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class Subscriber(Base):

    __tablename__ = "subscribers"
    __table_args__ = (
        UniqueConstraint("subscriber_id", "author_id", name="ux_sub"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    subscriber_id = Column(UUID(as_uuid=True), nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

