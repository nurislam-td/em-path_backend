from pydantic import BaseModel, ConfigDict


class VerifyOut(BaseModel):
    id: int
    email: str


class VerifyInDb(VerifyOut):
    model_config = ConfigDict(from_attributes=True)
    code: str
    is_active: bool


class VerifyCodeCreate(BaseModel):
    email: str
    code: str
    is_active: bool = True


class VerifyCodeCheck(BaseModel):
    id: int
    code: str


class VerifyCodeUpdate(VerifyCodeCreate):
    email: str | None = None
    code: str | None = None
    is_active: bool | None = None
