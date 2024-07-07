from typing import override

from sqlalchemy import select

from app.adapters.repo.base import AlchemyRepo
from app.schemas.verify_code import VerifyCodeDTO
from app.service.abstract.repo import VerifyCodeRepo


class AlchemyVerifyCodeSQLRepo(AlchemyRepo[VerifyCodeDTO], VerifyCodeRepo):
    @override
    async def get_last_active_by_email(self, email_in) -> VerifyCodeDTO | None:
        query = (
            select(self._table)
            .filter_by(email=email_in, is_active=True)
            .order_by(self._table.c.created_at.desc())
            .limit(1)
        )
        return await self.fetch_one(query)
