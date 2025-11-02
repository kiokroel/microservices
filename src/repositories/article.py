from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.article import Article
from src.repositories.base import BaseRepository
from src.schemas.article import ArticleCreate, ArticleUpdate


class ArticleRepository(BaseRepository[Article, ArticleCreate, ArticleUpdate]):
    """Репозиторий для работы со статьями"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Article)

    async def get_by_slug(
        self, slug: str, load_author: bool = False, load_comments: bool = False
    ) -> Optional[Article]:
        """Получить статью по slug"""
        stmt = select(Article).where(Article.slug == slug)
        if load_author:
            stmt = stmt.options(selectinload(Article.author))
        if load_comments:
            stmt = stmt.options(selectinload(Article.comments))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_author_id(
        self, author_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Article]:
        """Получить все статьи автора"""
        stmt = (
            select(Article)
            .where(Article.author_id == author_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def check_slug_exists(
        self, slug: str, exclude_id: Optional[UUID] = None
    ) -> bool:
        """Проверить, существует ли slug"""
        stmt = select(Article).where(Article.slug == slug)
        if exclude_id:
            stmt = stmt.where(Article.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
