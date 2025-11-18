from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.article import ArticleController
from src.core.database import get_db
from src.dependencies import get_current_user
from src.schemas.article import ArticleBase, ArticleResponse, ArticleUpdate
from src.services import enqueue_post_created

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_in: ArticleBase,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать новую статью"""
    controller = ArticleController(db)
    article = await controller.create_article(article_in, current_user["id"])
    await enqueue_post_created(current_user["id"], article.id)
    return article


@router.get("/", response_model=List[ArticleResponse])
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Получить список всех статей"""
    controller = ArticleController(db)
    return await controller.get_all_articles(skip, limit)


@router.get("/{slug}", response_model=ArticleResponse)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    """Получить статью по slug"""
    controller = ArticleController(db)
    article = await controller.get_article_by_slug(slug)
    return article


@router.put("/{slug}", response_model=ArticleResponse)
async def update_article(
    slug: str,
    article_update: ArticleUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить статью"""
    controller = ArticleController(db)
    return await controller.update_article(slug, article_update, current_user["id"])


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    slug: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить статью"""
    controller = ArticleController(db)
    await controller.delete_article(slug, current_user["id"])
    return None
