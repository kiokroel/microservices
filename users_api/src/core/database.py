from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

from src.core.config import settings

database_url = settings.database_url
echo = settings.api_settings.debug

engine = create_async_engine(
    database_url,
    echo=echo,
    pool_pre_ping=True,
    pool_size=settings.database_settings.db_pool_size,
)

# AsyncSessionLocal для создания асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base для ORM моделей
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для получения асинхронной сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
