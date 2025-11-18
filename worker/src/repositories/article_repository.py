from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.article import Article

class ArticleRepository:
    @staticmethod
    async def get_title_by_article_id(session: AsyncSession, article_id: UUID) -> str:
        stmt = select(Article.title).where(Article.id == article_id)
        result = await session.execute(stmt)
        row = result.fetchone()
        return row[0] if row else None
