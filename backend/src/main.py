import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import engine
from src.routes import router
from src.services import close_queue, init_queue

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
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    await init_queue()


@app.on_event("shutdown")
async def shutdown_event():
    await close_queue()


@app.get("/health")
def health_check():
    """Проверка здоровья приложения"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_settings.app_host,
        port=settings.api_settings.app_port,
    )
