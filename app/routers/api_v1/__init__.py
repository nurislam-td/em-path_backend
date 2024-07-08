from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as user_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(user_router)
api_router.include_router(auth_router)
