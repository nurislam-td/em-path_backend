import enum
from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String, text, types
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class User(Base):
    __tablename__ = "user"
    id: Mapped[UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()"),  # use what you have on your server
        index=True,
    )
    password: Mapped[bytes]
    email: Mapped[str] = mapped_column(String(length=255), index=True, unique=True)
    nickname: Mapped[str] = mapped_column(String(length=20))
    gender: Mapped[Gender] = mapped_column(Enum(Gender), default=Gender.other)
    name: Mapped[str | None]
    lastname: Mapped[str | None]
    patronymic: Mapped[str | None]
    date_birth: Mapped[datetime | None]
    image: Mapped[str | None]
    refresh_token: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="refresh_token")
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("(now() at time zone 'utc')"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("(now() at time zone 'utc')"),
        onupdate=text("(now() at time zone 'utc')"),
    )


class VerifyCode(Base):
    __tablename__ = "verify_code"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(length=255))
    code: Mapped[str] = mapped_column(String(length=6))
    is_active: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("(now() at time zone 'utc')"), nullable=False
    )
