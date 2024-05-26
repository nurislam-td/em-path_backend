from app.common.database import async_session_maker
from app.models.auth import RefreshToken, User, VerifyCode
from app.repo.token import AlchemyTokenSQLRepo
from app.repo.user import AlchemyUserSQLRepo
from app.repo.verify_code import AlchemyVerifyCodeSQLRepo
from app.schemas.token import TokenDTO
from app.schemas.user import UserDTO
from app.schemas.verify_code import VerifyCodeDTO
from app.service.abstract.unit_of_work import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    def __call__(self):
        return self

    async def __aenter__(self):
        self.session = self.session_factory()
        self.user = AlchemyUserSQLRepo(
            session=self.session,
            schema=UserDTO,
            model=User,
        )
        self.token = AlchemyTokenSQLRepo(
            session=self.session,
            schema=TokenDTO,
            model=RefreshToken,
        )
        self.verify_code = AlchemyVerifyCodeSQLRepo(
            session=self.session,
            schema=VerifyCodeDTO,
            model=VerifyCode,
        )

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
