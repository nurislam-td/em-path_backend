from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.common.exception_handler import (
    app_exception_handler,
    request_validation_exception_handler,
)
from app.common.exceptions import AppException
from app.common.settings import settings
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(settings.redis.url)
    FastAPICache.init(RedisBackend(redis), prefix=settings.redis.prefix)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def custom_request_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return await request_validation_exception_handler(request=request, exc=exc)


@app.exception_handler(AppException)
async def custom_app_exception_handler(
    request: Request, exc: AppException
) -> JSONResponse:
    return await app_exception_handler(request=request, exc=exc)


@app.get("/")
async def index():
    return {"message": "Root page"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
