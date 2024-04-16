from uuid import UUID

import pytest

from app.core.database import IUnitOfWork
from app.schemas.user import UserCreate, UserResetPassword


@pytest.mark.parametrize(
    "user_in",
    [
        UserCreate(
            nickname="melaton", email="coolest2@example.com", password="String03@"
        ),
        UserCreate(
            nickname="melaton", email="second2@example.com", password="String03@"
        ),
    ],
)
async def test_add_and_get_user_with_pydantic_model(
    user_in: UserCreate, uow: IUnitOfWork
):
    async with uow:
        assert not (await uow.user.get_by_email(email=user_in.email))
        user_created = await uow.user.create(user_in=user_in)
        await uow.commit()
        user_get = await uow.user.get(id=user_created["id"])
    assert user_created
    assert user_get["email"] == user_created["email"]


@pytest.mark.parametrize("email", ["user@example.com", "user4@example.com"])
async def test_get_user_by_email(email: str, uow: IUnitOfWork):
    async with uow:
        user_dict = await uow.user.get_by_email(email=email)
        assert user_dict
        assert user_dict["email"] == email


@pytest.mark.parametrize(
    "user_before, user_in",
    [
        (
            dict(
                nickname="string",
                email="userus@example.com",
                id="32ffa9be-e75e-4ebe-83d7-8d400c6c3bc7",
                password="$2b$12$pBXO3Qb8Q708eGJV3qyDCOMTwtK8I/2AI4xHzg7SsB8KEnPooWAly",
                sex="unknown",
                name=None,
                lastname=None,
                patronymic=None,
                date_birth=None,
                image=None,
            ),
            dict(
                name="Mark",
                lastname="Avreli",
            ),
        )
    ],
)
async def test_user_update(user_before, user_in, uow: IUnitOfWork):
    async with uow:
        updated_user = await uow.user.update(
            values=user_in, filters=dict(id=user_before["id"])
        )
        await uow.commit()
        user_data = await uow.user.get(id=user_before["id"])
        assert user_data == updated_user
        assert user_before != updated_user


@pytest.mark.parametrize(
    "password_before, user_in, user_id",
    [
        (
            "$2b$12$pBXO3Qb8Q708eGJV3qyDCOMTwtK8I/2AI4xHzg7SsB8KEnPooWAly",
            UserResetPassword(email="userus@example.com", password="SomePassHard98$"),
            "32ffa9be-e75e-4ebe-83d7-8d400c6c3bc7",
        ),
    ],
)
async def test_reset_password(
    password_before, user_in: UserResetPassword, user_id: UUID, uow: IUnitOfWork
):
    async with uow:
        user_dict = await uow.user.reset_password(user_in=user_in, user_id=user_id)
        assert user_dict["password"] != password_before


@pytest.mark.parametrize("user_id", ["ae538ea8-0cc0-4e06-9649-f5fa7c28701b"])
async def test_user_delete(user_id: UUID, uow: IUnitOfWork):
    async with uow:
        assert not (await uow.user.delete(dict(id=user_id)))
        assert not (await uow.user.get(id=user_id))
