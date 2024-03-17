from abc import ABC, abstractmethod
from typing import Type

from core.settings import settings
from repo.token import TokenRepo
from repo.user import UserRepo
from repo.verify_code import VerifyCodeRepo
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(url=settings.db.url)
async_session_maker = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False
)


class IUnitOfWork(ABC):
    user: Type[UserRepo]
    token: Type[TokenRepo]
    verify_code: Type[VerifyCodeRepo]

    @abstractmethod
    async def __init__(self):
        raise NotImplementedError

    @abstractmethod
    async def __call__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    def __call__(self):
        return self

    async def __aenter__(self):
        self.session = self.session_factory()
        self.user = UserRepo(session=self.session)
        self.token = TokenRepo(session=self.session)
        self.verify_code = VerifyCodeRepo(session=self.session)

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
