from models.auth import VerifyCode
from repo.base import SQLAlchemyRepo
from sqlalchemy import select


class VerifyCodeRepo(SQLAlchemyRepo):
    model = VerifyCode

    async def get_by_email(self, email_in):
        query = select(self.model.__table__).filter_by(email=email_in)
        return await self.fetch_one(query)
