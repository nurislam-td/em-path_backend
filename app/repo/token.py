from typing import override

from sqlalchemy import select

from app.models.auth import RefreshToken
from app.repo.base import SQLAlchemyRepo
from app.schemas.token import TokenDTO
from app.service.interfaces.repo import ISQLTokenRepo


class TokenRepo(SQLAlchemyRepo[TokenDTO, RefreshToken], ISQLTokenRepo):
    @override
    async def get_by_user_id(self, user_id) -> TokenDTO:
        query = select(self._table).filter_by(user_id=user_id)
        return await self.fetch_one(query)

    @override
    async def save_token(self, user_id, refresh_token) -> TokenDTO:
        refresh_token_dto: TokenDTO = await self.get_by_user_id(user_id=user_id)
        if refresh_token_dto:
            return await self.update_one(
                values={"refresh_token": refresh_token},
                pk=refresh_token_dto.id,
            )

        return await self.create(
            values={"user_id": user_id, "refresh_token": refresh_token}
        )
