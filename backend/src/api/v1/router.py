from fastapi import APIRouter

from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router
from src.api.v1.posts import router as posts_router
from src.api.v1.admin import router as admin_router
from src.api.v1.categories import router as categories_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(posts_router)
api_router.include_router(categories_router)
api_router.include_router(admin_router)
