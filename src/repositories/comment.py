from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment
from src.repositories.base import BaseRepository
from src.schemas.comment import CommentCreate


class CommentRepository(BaseRepository[Comment, CommentCreate, CommentCreate]):
    """Репозиторий для работы с комментариями"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Comment)

    async def get_by_article_id(
        self, article_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Comment]:
        """Получить все комментарии статьи"""
        stmt = (
            select(Comment)
            .where(Comment.article_id == article_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_article_and_comment_id(
        self, article_id: UUID, comment_id: UUID
    ) -> Optional[Comment]:
        """Получить комментарий статьи по ID"""
        stmt = select(Comment).where(
            Comment.article_id == article_id, Comment.id == comment_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
