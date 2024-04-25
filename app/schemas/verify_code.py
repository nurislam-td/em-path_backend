from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class VerifyOut(BaseModel):
    id: int
    email: EmailStr


class VerifyCodeDTO(VerifyOut):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    code: str
    is_active: bool
    created_at: datetime


class VerifyCodeCreate(BaseModel):
    email: EmailStr
    code: str
    is_active: bool = True


class VerifyCodeCheck(BaseModel):
    email: EmailStr
    code: str


class VerifyCodeUpdate(VerifyCodeCreate):
    email: EmailStr | None = None
    code: str | None = None
    is_active: bool | None = None
