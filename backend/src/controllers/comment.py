from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.article import ArticleRepository
from src.repositories.comment import CommentRepository
from src.schemas.comment import CommentBase, CommentCreate


class CommentController:

    def __init__(self, db: AsyncSession):
        self.comment_repo = CommentRepository(db)
        self.article_repo = ArticleRepository(db)

    async def create_comment(self, slug: str, comment_in: CommentBase, author_id: UUID):
        article = await self.article_repo.get_by_slug(slug)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена"
            )

        comment_data = comment_in.model_dump()
        comment_data["article_id"] = article.id
        comment_data["author_id"] = author_id
        comment = await self.comment_repo.create(CommentCreate(**comment_data))
        return comment

    async def get_article_comments(self, slug: str, skip: int = 0, limit: int = 20):
        article = await self.article_repo.get_by_slug(slug)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена"
            )
        return await self.comment_repo.get_by_article_id(article.id, skip, limit)

    async def delete_comment(
        self, slug: str, comment_id: UUID, author_id: UUID
    ) -> bool:
        article = await self.article_repo.get_by_slug(slug)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена"
            )

        comment = await self.comment_repo.get_by_article_and_comment_id(
            article.id, comment_id
        )
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
            )

        if comment.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете удалять чужой комментарий",
            )

        return await self.comment_repo.delete(comment_id)
