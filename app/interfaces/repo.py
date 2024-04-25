from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import DeclarativeBase

from app.models.auth import RefreshToken, User, VerifyCode
from app.schemas.token import TokenDTO
from app.schemas.user import UserCreate, UserDTO, UserResetPassword
from app.schemas.verify_code import VerifyCodeDTO

DTOSchema = TypeVar("DTOSchema", bound=BaseModel)
DBModel = TypeVar("DBModel", bound=DeclarativeBase)


class IRepo(ABC):
    @abstractmethod
    async def create(self) -> DTOSchema: ...

    @abstractmethod
    async def get_all(self) -> list[DTOSchema]: ...

    @abstractmethod
    async def get(self) -> DTOSchema: ...

    @abstractmethod
    async def update(self) -> list[DTOSchema]: ...

    @abstractmethod
    async def update_one(self) -> DTOSchema: ...

    @abstractmethod
    async def delete(self) -> None: ...


class ISQLRepo(IRepo, Generic[DTOSchema, DBModel]):
    @abstractmethod
    def __init__(self, session, schema: DTOSchema, model: DBModel) -> None: ...

    @abstractmethod
    async def create(self, values: dict) -> DTOSchema | None: ...

    @abstractmethod
    async def get_all(self, **kwargs) -> list[DTOSchema] | None: ...

    @abstractmethod
    async def get(self, pk: UUID | int) -> DTOSchema | None: ...

    @abstractmethod
    async def update(self, values: dict, filters: dict) -> list[DTOSchema] | None: ...

    @abstractmethod
    async def update_one(self, values: dict, pk: UUID | int) -> DTOSchema | None: ...

    @abstractmethod
    async def delete(self, filters: dict) -> None: ...


class ISQLTokenRepo(ISQLRepo[TokenDTO, RefreshToken]):

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> TokenDTO | None: ...

    @abstractmethod
    async def saveToken(self, user_id: UUID, refresh_token: str) -> TokenDTO | None: ...


class ISQLUserRepo(ISQLRepo[UserDTO, User]):
    @abstractmethod
    async def get_by_email(self, email: EmailStr) -> UserDTO | None: ...

    @abstractmethod
    async def create(self, user_in: UserCreate) -> UserDTO | None: ...

    @abstractmethod
    async def reset_password(
        self, user_in: UserResetPassword, user_id: UUID
    ) -> UserDTO | None: ...


class ISQLVerifyCodeRepo(ISQLRepo[VerifyCodeDTO, VerifyCode]):
    @abstractmethod
    async def get_last_active_by_email(
        self, email: EmailStr
    ) -> VerifyCodeDTO | None: ...
