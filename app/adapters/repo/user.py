from typing import override
from uuid import UUID

from sqlalchemy import select

from app.adapters.repo.base import AlchemyRepo
from app.models import User
from app.schemas.user import UserCreate, UserDTO, UserResetPassword
from app.service.abstract.repo import UserRepo
from app.service.secure import get_password_hash


class AlchemyUserSQLRepo(AlchemyRepo[UserDTO], UserRepo):
    _model = User
    _schema = UserDTO

    @override
    async def get_by_email(self, email) -> UserDTO | None:
        query = select(self._table).filter_by(email=email)
        return await self.fetch_one(query)

    @override
    async def create(self, user_in: UserCreate) -> UserDTO | None:
        user_in.password = get_password_hash(user_in.password)
        return await super().create(user_in.model_dump())

    @override
    async def reset_password(
        self, user_in: UserResetPassword, user_id: UUID
    ) -> UserDTO | None:
        user_in.password = get_password_hash(user_in.password)
        return await super().update_one(pk=user_id, values=user_in.model_dump())
