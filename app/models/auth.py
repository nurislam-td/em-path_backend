from datetime import datetime
import enum
from typing import List
from uuid import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import ForeignKey, types, text, Enum, String, func
from .base import Base


class Sex(enum.Enum):
    male = "Male"
    female = "Female"
    unknown = "Unknown"


class User(Base):
    __tablename__ = "user"
    user_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        server_default=text("gen_random_uuid()"),  # use what you have on your server
        index=True,
    )
    nickname: Mapped[str] = mapped_column(String(length=12))
    password: Mapped[bytes] = mapped_column()
    email: Mapped[str] = mapped_column(String(length=255), index=True, unique=True)
    sex: Mapped[Sex] = mapped_column(Enum(Sex), default=Sex.unknown)
    name: Mapped[str | None] = mapped_column(default=None)
    lastname: Mapped[str | None] = mapped_column(default=None)
    patronymic: Mapped[str | None] = mapped_column(default=None)
    date_birth: Mapped[datetime | None] = mapped_column(default=None)
    image: Mapped[str | None] = mapped_column(default=None)
    refresh_token: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", cascade="all,delete"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_token"
    rt_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.user_id"))
    user: Mapped["User"] = relationship(back_populates="refresh_token")
    refresh_token: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class VerifyCode(Base):
    __tablename__ = "verify_code"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(length=255))
    code: Mapped[str] = mapped_column(String(length=6))
    is_active: Mapped[bool] = mapped_column()
