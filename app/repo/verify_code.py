from typing import override

from sqlalchemy import select

from app.models.auth import VerifyCode
from app.repo.base import SQLAlchemyRepo
from app.schemas.verify_code import VerifyCodeDTO
from app.service.interfaces.repo import ISQLVerifyCodeRepo


class VerifyCodeRepo(SQLAlchemyRepo[VerifyCodeDTO, VerifyCode], ISQLVerifyCodeRepo):
    @override
    async def get_last_active_by_email(self, email_in) -> VerifyCodeDTO | None:
        query = (
            select(self._table)
            .filter_by(email=email_in, is_active=True)
            .order_by(self._table.c.created_at.desc())
            .limit(1)
        )
        return await self.fetch_one(query)
