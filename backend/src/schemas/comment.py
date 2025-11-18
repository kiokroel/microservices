from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """Базовая схема комментария"""
    body: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    """Схема для создания комментария"""

    article_id: UUID
    author_id: UUID


class CommentResponse(CommentBase):
    """Схема ответа комментария"""

    id: UUID
    article_id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
