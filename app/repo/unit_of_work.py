from app.core.database import async_session_maker
from app.interfaces.unit_of_work import IUnitOfWork
from app.models.auth import RefreshToken, User, VerifyCode
from app.repo.token import TokenRepo
from app.repo.user import UserRepo
from app.repo.verify_code import VerifyCodeRepo
from app.schemas.token import TokenDTO
from app.schemas.user import UserDTO
from app.schemas.verify_code import VerifyCodeDTO


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    def __call__(self):
        return self

    async def __aenter__(self):
        self.session = self.session_factory()
        self.user = UserRepo(
            session=self.session,
            schema=UserDTO,
            model=User,
        )
        self.token = TokenRepo(
            session=self.session,
            schema=TokenDTO,
            model=RefreshToken,
        )
        self.verify_code = VerifyCodeRepo(
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
