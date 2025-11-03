from uuid import UUID

from fastapi import HTTPException, status
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.article import ArticleRepository
from src.schemas.article import (ArticleBase, ArticleCreate, ArticleResponse,
                                 ArticleUpdate)


class ArticleController:
    def __init__(self, db: AsyncSession):
        self.article_repo = ArticleRepository(db)

    async def _generate_slug(self, title: str, exclude_id: UUID = None) -> str:
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while await self.article_repo.check_slug_exists(slug, exclude_id):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    async def create_article(self, article_in: ArticleBase, author_id: UUID):
        slug = await self._generate_slug(article_in.title)
        article_data = article_in.model_dump()
        article_data["slug"] = slug
        article_data["author_id"] = author_id
        article_data["tag_list"] = (
            ",".join(article_in.tag_list) if article_in.tag_list else None
        )
        article = await self.article_repo.create(ArticleCreate(**article_data))
        article_resp_data = article.__dict__
        article_resp_data["tag_list"] = (
            article.tag_list.split(",") if article.tag_list else []
        )
        article_response = ArticleResponse.model_validate(article_resp_data)
        return article_response

    async def get_all_articles(self, skip: int = 0, limit: int = 20):
        articles = await self.article_repo.get_all(skip, limit)
        return [
            ArticleResponse(
                id=article.id,
                title=article.title,
                slug=article.slug,
                description=article.description,
                body=article.body,
                tag_list=article.tag_list.split(",") if article.tag_list else [],
                created_at=article.created_at,
                updated_at=article.updated_at,
                author_id=article.author_id,
            )
            for article in articles
        ]

    async def get_article_by_slug(self, slug: str):
        article = await self.article_repo.get_by_slug(slug, load_author=True)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена"
            )
        article_resp_data = article.__dict__
        article_resp_data["tag_list"] = (
            article.tag_list.split(",") if article.tag_list else []
        )
        article_response = ArticleResponse.model_validate(article_resp_data)
        return article_response

    async def update_article(
        self, slug: str, article_update: ArticleUpdate, author_id: UUID
    ):
        article = await self.article_repo.get_by_slug(slug)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена"
            )

        if article.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете редактировать чужую статью",
            )

        if article_update.title:
            new_slug = await self._generate_slug(article_update.title, article.id)
            article.slug = new_slug  # type: ignore

        if article_update.tag_list is not None:
            article_update.tag_list = ",".join(article_update.tag_list)  # type: ignore

        updated_article = await self.article_repo.update(article, article_update)
        article_resp_data = updated_article.__dict__
        article_resp_data["tag_list"] = (
            updated_article.tag_list.split(",") if updated_article.tag_list else []
        )
        article_response = ArticleResponse.model_validate(article_resp_data)
        return article_response

    async def delete_article(self, slug: str, author_id: UUID) -> bool:
        article = await self.article_repo.get_by_slug(slug)
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена"
            )

        if article.author_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не можете удалять чужую статью",
            )

        return await self.article_repo.delete(article.id)
