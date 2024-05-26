from uuid import UUID

import pytest

from app.core.exceptions import UserAlreadyExistsException, UserNotExistsException
from app.repo.unit_of_work import SQLAlchemyUnitOfWork
from app.schemas.token import JWTPayload
from app.schemas.user import UserCreate, UserResetPassword
from app.service import user


async def test_create_user(uow: SQLAlchemyUnitOfWork):
    user_create = UserCreate(
        email="userService@mail.com", password="String03@", nickname="test"
    )
    user_dto = await user.create_user(user_data=user_create, uow=uow)
    assert user_dto.email == "userService@mail.com"


async def test_already_exist_user_create(uow: SQLAlchemyUnitOfWork):
    user_create = UserCreate(
        email="user@example.com", password="String03@", nickname="test"
    )
    with pytest.raises(UserAlreadyExistsException):
        await user.create_user(user_data=user_create, uow=uow)


async def test_login_user(uow: SQLAlchemyUnitOfWork):
    async with uow:
        user_dto = await uow.user.get_by_email("user@example.com")
        assert user_dto is not None, "USER NOT EXISTS"
    tokens = await user.login(user_data=user_dto, uow=uow)
    assert tokens is not None, "TOKENS NOT EXISTS"


async def test_refresh_user_token(uow: SQLAlchemyUnitOfWork):
    jwt_payload = JWTPayload(
        email="user@example.com", sub=UUID("ae538ea8-0cc0-4e06-9649-f5fa7c28701b")
    )
    tokens = await user.refresh_tokens(jwt_payload=jwt_payload, uow=uow)
    assert tokens is not None, "TOKENS NOT EXISTS"


async def test_reset_user_password(uow: SQLAlchemyUnitOfWork):
    user_in = UserResetPassword(email="user@example.com", password="String03@")
    user_dto = await user.reset_password(uow=uow, update_data=user_in)
    assert user_dto, "Failed to reset password"


async def test_fail_reset_user_password(uow: SQLAlchemyUnitOfWork):
    user_in = UserResetPassword(email="unknown@example.com", password="String03@")
    with pytest.raises(UserNotExistsException):
        await user.reset_password(uow=uow, update_data=user_in)
