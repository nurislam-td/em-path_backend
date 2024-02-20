from .base import CRUDBase
from auth import VerifyCode
from schemas.verify_code import VerifyCodeCreate, VerifyCodeUpdate


class CRUDVerifyCode(CRUDBase[VerifyCode, VerifyCodeCreate, VerifyCodeUpdate]):
    pass


verify_code = CRUDVerifyCode(VerifyCode)
