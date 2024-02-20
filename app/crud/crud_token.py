from sqlalchemy import Result, select
from .base import CRUDBase
from models.auth import RefreshToken
from schemas.token import RefreshTokenCreate, RefreshTokenUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDToken(CRUDBase[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate]):
    async def get_by_user_id(self, db: AsyncSession, *, user_id) -> RefreshToken | None:
        token_res: Result = await db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        return token_res.scalars().one_or_none()


token = CRUDToken(RefreshToken)
