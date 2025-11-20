from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

from src.core.config import settings

users_api_engine = create_async_engine(
    url=settings.users_api_settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.users_api_settings.db_pool_size,
)

backend_api_engine = create_async_engine(
    url=settings.backend_api_settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.backend_api_settings.db_pool_size,
)

worker_engine = create_async_engine(
    url=settings.worker_db_settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.worker_db_settings.db_pool_size,
)

# AsyncSessionLocal для создания асинхронных сессий
UsersAsyncSessionLocal = async_sessionmaker(
    users_api_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

BackendAsyncSessionLocal = async_sessionmaker(
    backend_api_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

WorkerAsyncSessionLocal = async_sessionmaker(
    worker_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

UsersBase = declarative_base()
BackendBase = declarative_base()
WorkerBase = declarative_base()


async def get_users_db() -> AsyncGenerator[AsyncSession, None]:
    async with UsersAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_backend_db() -> AsyncGenerator[AsyncSession, None]:
    async with BackendAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_worker_db() -> AsyncGenerator[AsyncSession, None]:
    async with WorkerAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()