from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
import re

STRONG_PASSWORD_PATTERN = re.compile(
    r"(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,128}"
)


class Sex(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


class UserOut(BaseModel):
    nickname: str
    email: EmailStr


class UserCreate(UserOut):
    password: str = Field(min_length=6, max_length=128)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit and "
                "special symbol"
            )
        return password


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    nickname: str | None = None
    sex: Sex | None = None
    name: str | None = None
    lastname: str | None = None
    patronymic: str | None = None
    date_birth: str | None = None
    image: str | None = None

    @model_validator(mode="after")
    def validate_model(self):
        if not any(v for v in self.model_dump().values()):
            raise ValueError("At least one field must be filled in")
        return self


class UserResetPassword(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit and "
                "special symbol"
            )
        return password


class UserDTO(UserOut):
    id: UUID
    password: bytes
    sex: Sex | None = Sex.unknown
    name: str | None = None
    lastname: str | None = None
    patronymic: str | None = None
    date_birth: datetime | None = None
    image: str | None = None
