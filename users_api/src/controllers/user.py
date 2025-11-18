from datetime import timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import security_service
from src.repositories.subscriber import SubscriberRepository
from src.repositories.user import UserRepository
from src.schemas.user import (SubscribeRequest, SubscriptionKeyUpdate, UserCreate,
                              UserLogin, UserUpdate)

jwt_settings = settings.jwt_settings


class UserController:

    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.subscriber_repo = SubscriberRepository(db)

    async def register(self, user_in: UserCreate):
        if await self.user_repo.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует",
            )
        if await self.user_repo.get_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким username уже существует",
            )

        user = await self.user_repo.create_with_password(user_in)
        return user

    async def login(self, credentials: UserLogin):
        user = await self.user_repo.authenticate(
            credentials.email, credentials.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
            )

        access_token_expires = timedelta(hours=jwt_settings.expiration_hours)
        access_token = security_service.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "user": user}

    async def get_current_user(self, user_id: UUID):
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )
        return user

    async def update_user(self, user_id: UUID, user_update: UserUpdate):
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )

        if user_update.email and user_update.email != user.email:
            if await self.user_repo.get_by_email(user_update.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email уже используется",
                )

        if user_update.username and user_update.username != user.username:
            if await self.user_repo.get_by_username(user_update.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username уже используется",
                )

        updated_user = await self.user_repo.update(user, user_update)
        return updated_user

    async def update_subscription_key(
        self, user_id: UUID, payload: SubscriptionKeyUpdate
    ):
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
            )

        user.subscription_key = payload.subscription_key
        self.user_repo.db.add(user)
        await self.user_repo.db.commit()
        await self.user_repo.db.refresh(user)
        return user

    async def subscribe_to_author(
        self, subscriber_id: UUID, request: SubscribeRequest
    ) -> None:
        if subscriber_id == request.target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя подписаться на самого себя",
            )

        target_user = await self.user_repo.get(request.target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь для подписки не найден",
            )

        existing = await self.subscriber_repo.get_subscription(
            subscriber_id, request.target_user_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Подписка уже существует",
            )

        await self.subscriber_repo.create_subscription(
            subscriber_id=subscriber_id, author_id=request.target_user_id
        )
