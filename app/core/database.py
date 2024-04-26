from sqlalchemy import NullPool, create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.settings import settings

if settings.MODE == "DEV":
    DATABASE_URL = settings.db.url
    DATABASE_PARAMS = {}
else:
    DATABASE_URL = settings.db.test_url
    DATABASE_PARAMS = {"poolclass": NullPool}


async_engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)
async_session_maker = async_sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False
)

engine = create_engine(settings.db.sync_url, **DATABASE_PARAMS)
