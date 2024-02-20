from .auth import router as auth_router
from fastapi import APIRouter

api_router = APIRouter(prefix="/api_v1")
api_router.include_router(auth_router)
