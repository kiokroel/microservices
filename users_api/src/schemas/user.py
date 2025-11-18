from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    """Базовая схема пользователя"""
    username: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    bio: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    subscription_key: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""

    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""

    username: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    bio: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    subscription_key: Optional[str] = None


class SubscriptionKeyUpdate(BaseModel):
    """Обновление subscription_key"""

    subscription_key: str = Field(..., min_length=1)


class SubscribeRequest(BaseModel):
    """Тело запроса на подписку"""

    target_user_id: UUID


class UserLogin(BaseModel):
    """Схема для логина"""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Схема ответа пользователя"""

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserLoginResponse(BaseModel):
    """Схема ответа при логине"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
