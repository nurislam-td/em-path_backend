from repo.base import SQLAlchemyRepo
from models.auth import VerifyCode


class VerifyCodeRepo(SQLAlchemyRepo):
    model = VerifyCode
