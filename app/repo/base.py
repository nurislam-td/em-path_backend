from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import (
    Delete,
    Insert,
    Result,
    Select,
    Update,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class AbstractRepo(ABC):
    @abstractmethod
    async def create(self):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

    @abstractmethod
    async def get(self):
        raise NotImplementedError

    @abstractmethod
    async def update(self):
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        raise NotImplementedError


class SQLAlchemyRepo(AbstractRepo):
    model: DeclarativeBase = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_one(self, query: Select | Insert | Update) -> dict[str, Any] | None:
        result: Result = await self.session.execute(query)
        return result.mappings().one_or_none()

    async def fetch_all(self, query: Select | Insert | Update) -> list[dict[str, Any]]:
        result: Result = await self.session.execute(query)
        return list(result.mappings().all())

    async def execute(self, query: Insert | Update | Delete) -> None:
        await self.session.execute(query)

    async def create(self, values: dict) -> dict[str, Any]:
        query = insert(self.model.__table__).values(**values).returning(self.model)
        return await self.fetch_one(query)

    async def get_all(self, **kwargs) -> list[dict[str, Any]]:
        query = select(self.model.__table__).filter_by(**kwargs)
        return await self.fetch_all(query)

    async def get(self, id) -> dict[str, Any]:
        query = select(self.model.__table__).filter_by(id=id)
        return await self.fetch_one(query)

    async def update(self, values: dict, filters: dict) -> dict[str, Any]:
        query = (
            update(self.model.__table__)
            .filter_by(**filters)
            .values(**values)
            .returning(self.model)
        )
        return await self.fetch_one(query)

    async def delete(self, filters: dict) -> None:
        query = delete(self.model.__table__).filter_by(**filters)
        return await self.execute(query)
