from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from src.schemas.user import UserResponse


class ArticleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """Базовая схема статьи"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=500)
    body: str = Field(...)
    tag_list: Optional[List[str]] = None


class ArticleCreate(ArticleBase):
    """Схема для создания статьи"""

    slug: str
    author_id: UUID
    tag_list: Optional[str] = None

    pass


class ArticleUpdate(BaseModel):
    """Схема для обновления статьи"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    body: Optional[str] = None
    tag_list: Optional[List[str]] = None


class ArticleResponse(ArticleBase):
    """Схема ответа статьи"""

    id: UUID
    slug: str
    author_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
