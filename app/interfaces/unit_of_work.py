from abc import ABC, abstractmethod
from typing import Type

from app.interfaces.repo import ISQLTokenRepo, ISQLUserRepo, ISQLVerifyCodeRepo


class IUnitOfWork(ABC):
    user: ISQLUserRepo
    token: ISQLTokenRepo
    verify_code: ISQLVerifyCodeRepo

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __call__(self): ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...
