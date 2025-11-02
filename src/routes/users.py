from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.user import UserController
from src.core.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.user import (UserCreate, UserLogin, UserLoginResponse,
                              UserResponse, UserUpdate)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя"""
    controller = UserController(db)
    user = await controller.register(user_in)
    return user


@router.post("/login", response_model=UserLoginResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Логин пользователя"""
    controller = UserController(db)
    return await controller.login(credentials)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить информацию о текущем пользователе"""
    controller = UserController(db)
    return await controller.update_user(current_user.id, user_update)
