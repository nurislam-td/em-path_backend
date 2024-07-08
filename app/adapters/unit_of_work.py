from app.adapters.repo.token import AlchemyTokenSQLRepo
from app.adapters.repo.user import AlchemyUserSQLRepo
from app.adapters.repo.verify_code import AlchemyVerifyCodeSQLRepo
from app.common.database import async_session_maker
from app.service.abstract.unit_of_work import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    def __call__(self):
        return self

    async def __aenter__(self):
        self.session = self.session_factory()
        self.user = AlchemyUserSQLRepo(session=self.session)
        self.token = AlchemyTokenSQLRepo(session=self.session)
        self.verify_code = AlchemyVerifyCodeSQLRepo(session=self.session)

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
