from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.subscriber import Subscriber


class SubscriberRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_subscription(
        self, subscriber_id: UUID, author_id: UUID
    ) -> Optional[Subscriber]:
        stmt = select(Subscriber).where(
            Subscriber.subscriber_id == subscriber_id,
            Subscriber.author_id == author_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_subscription(self, subscriber_id: UUID, author_id: UUID) -> Subscriber:
        subscription = Subscriber(subscriber_id=subscriber_id, author_id=author_id)
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

