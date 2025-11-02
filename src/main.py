import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import Base, engine
from src.routes import articles, comments, users

# Инициализировать приложение
app = FastAPI(
    title=settings.api_settings.api_title,
    description=settings.api_settings.api_description,
    version=settings.api_settings.api_version,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Роуты
app.include_router(users.router)
app.include_router(articles.router)
app.include_router(comments.router)


@app.get("/health")
def health_check():
    """Проверка здоровья приложения"""
    return {"status": "ok"}


async def init_db():
    """Создать все таблицы в базе данных"""
    print(f"Connecting to: {settings.database_url}")
    # Если есть такие поля в настройках, можно вывести
    # print(f"User: {settings.database_settings.postgres_user}")
    # print(f"DB: {settings.database_settings.postgres_db}")

    async with engine.begin() as conn:
        # Удалить все таблицы (опционально)
        # await conn.run_sync(Base.metadata.drop_all)

        # Создать все таблицы
        await conn.run_sync(Base.metadata.create_all)

    print("✅ База данных успешно инициализирована!")


if __name__ == "__main__":
    # Инициализация БД перед стартом сервера
    asyncio.run(init_db())

    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_settings.app_host,
        port=settings.api_settings.app_port,
    )
