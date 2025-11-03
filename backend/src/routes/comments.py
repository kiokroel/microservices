from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.comment import CommentController
from src.core.database import get_db
from src.dependencies import get_current_user
from src.schemas.comment import CommentBase, CommentResponse

router = APIRouter(prefix="/api/articles", tags=["comments"])


@router.post(
    "/{slug}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    slug: str,
    comment_in: CommentBase,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Добавить комментарий к статье"""
    controller = CommentController(db)
    return await controller.create_comment(slug, comment_in, current_user["id"])


@router.get("/{slug}/comments", response_model=List[CommentResponse])
async def get_comments(
    slug: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Получить комментарии статьи"""
    controller = CommentController(db)
    return await controller.get_article_comments(slug, skip, limit)


@router.delete("/{slug}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    slug: str,
    comment_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить комментарий"""
    controller = CommentController(db)
    await controller.delete_comment(slug, comment_id, current_user["id"])
    return None
