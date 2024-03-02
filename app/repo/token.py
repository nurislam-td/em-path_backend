from sqlalchemy import select
from .base import SQLAlchemyRepo
from models.auth import RefreshToken


class TokenRepo(SQLAlchemyRepo):
    model = RefreshToken

    async def get_by_user_id(self, user_id):
        query = select(self.model.__table__).filter_by(user_id=user_id)
        return await self.fetch_one(query)

    async def saveToken(self, user_id, refresh_token):
        refresh_token_obj = await self.get_by_user_id(user_id=user_id)
        if refresh_token_obj:
            return await self.update(
                values={"refresh_token": refresh_token},
                filters={"id": refresh_token_obj["id"]},
            )
        return await self.create(
            values={"user_id": user_id, "refresh_token": refresh_token}
        )
