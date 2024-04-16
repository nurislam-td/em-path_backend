from pydantic import BaseModel, ConfigDict, EmailStr


class VerifyOut(BaseModel):
    id: int
    email: EmailStr


class VerifyInDb(VerifyOut):
    model_config = ConfigDict(from_attributes=True)
    code: str
    is_active: bool


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
