from abc import abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.schemas.token import TokenDTO
from app.schemas.user import UserCreate, UserDTO, UserResetPassword
from app.schemas.verify_code import VerifyCodeDTO

DTOSchema = TypeVar("DTOSchema", bound=BaseModel)


class Repo(Generic[DTOSchema]):
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


class TokenRepo(Repo[TokenDTO]):
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> TokenDTO | None: ...

    @abstractmethod
    async def save_token(
        self, user_id: UUID, refresh_token: str
    ) -> TokenDTO | None: ...


class UserRepo(Repo[UserDTO]):
    @abstractmethod
    async def get_by_email(self, email: EmailStr) -> UserDTO | None: ...

    @abstractmethod
    async def create(self, user_in: UserCreate) -> UserDTO | None: ...

    @abstractmethod
    async def reset_password(
        self, user_in: UserResetPassword, user_id: UUID
    ) -> UserDTO | None: ...


class VerifyCodeRepo(Repo[VerifyCodeDTO]):
    @abstractmethod
    async def get_last_active_by_email(
        self, email_in: EmailStr
    ) -> VerifyCodeDTO | None: ...
