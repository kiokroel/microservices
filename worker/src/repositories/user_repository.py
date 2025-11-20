from typing import Dict, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.subscriber import Subscriber
from src.models.user import User

class UserRepository:
    async def get_subscribers_by_author_id(session: AsyncSession, author_id: UUID) -> List[UUID]:
        stmt = select(Subscriber.subscriber_id).where(Subscriber.author_id == author_id)
        result = await session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    @staticmethod
    async def get_users_subscription_keys_by_ids(session: AsyncSession, user_ids: List[UUID]) -> Dict[UUID, str]:
        if not user_ids:
            return {}
        stmt = select(User.id, User.subscription_key).where(User.id.in_(user_ids))
        result = await session.execute(stmt)
        return {row[0]: row[1] for row in result.fetchall()}
