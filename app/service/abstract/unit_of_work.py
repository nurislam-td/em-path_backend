from abc import ABC, abstractmethod

from app.service.abstract.repo import TokenRepo, UserRepo, VerifyCodeRepo


class UnitOfWork(ABC):
    user: UserRepo
    token: TokenRepo
    verify_code: VerifyCodeRepo

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
