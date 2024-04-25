from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.settings import settings

if settings.MODE == "DEV":
    DATABASE_URL = settings.db.url
    DATABASE_PARAMS = {}
else:
    DATABASE_URL = settings.db.test_url
    DATABASE_PARAMS = {"poolclass": NullPool}


engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)
async_session_maker = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False
)
