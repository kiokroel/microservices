from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notifications_sent import NotificationSent


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def was_sent(self, subscriber_id: UUID, post_id: UUID) -> bool:
        stmt = (
            select(NotificationSent.id)
            .where(
                NotificationSent.subscriber_id == subscriber_id,
                NotificationSent.post_id == post_id,
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def mark_sent(self, subscriber_id: UUID, post_id: UUID) -> None:
        entity = NotificationSent(
            subscriber_id=subscriber_id,
            post_id=post_id,
        )
        self._session.add(entity)
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()

