from sqlalchemy import select

from app.models.auth import VerifyCode
from app.repo.base import SQLAlchemyRepo


class VerifyCodeRepo(SQLAlchemyRepo):
    model = VerifyCode

    async def get_last_active_by_email(self, email_in):
        query = (
            select(self.model.__table__)
            .filter_by(email=email_in, is_active=True)
            .order_by(self.model.__table__.c.created_at.desc())
            .limit(1)
        )
        return await self.fetch_one(query)
