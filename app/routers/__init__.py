from fastapi import APIRouter

from app.routers.api_v1 import api_router as v1_router

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)
