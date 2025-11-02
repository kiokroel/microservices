from .articles import router as articles_router
from .users import router as users_router
from .comments import router as comments_router

from fastapi import APIRouter

router = APIRouter()
router.include_router(articles_router)
router.include_router(users_router)
router.include_router(comments_router)

__all__ = ["router"]
