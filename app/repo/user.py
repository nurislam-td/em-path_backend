from uuid import UUID

from sqlalchemy import select

from app.models.auth import User
from app.repo.base import SQLAlchemyRepo
from app.schemas.user import UserCreate, UserResetPassword
from app.service.secure import get_password_hash


class UserRepo(SQLAlchemyRepo):
    model = User

    async def get_by_email(self, email):
        query = select(self.model.__table__).filter_by(email=email)
        return await self.fetch_one(query)

    async def create(self, user_in: UserCreate):
        user_in.password = get_password_hash(user_in.password)
        return await super().create(user_in.model_dump())

    async def reset_password(self, user_in: UserResetPassword, user_id: UUID):
        user_in.password = get_password_hash(user_in.password)
        return await super().update_one(id=user_id, values=user_in.model_dump())
