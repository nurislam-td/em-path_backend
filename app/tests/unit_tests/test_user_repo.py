import pytest
from schemas.user import UserCreate

from app.core.database import IUnitOfWork


@pytest.mark.parametrize(
    "nickname, email, password",
    [
        ("melaton", "cool@example.com", "String03@"),
        ("melaton", "second@example.com", "String03@"),
    ],
)
async def test_add_and_get_user(nickname, email, password, uow: IUnitOfWork):
    user_in = UserCreate(nickname=nickname, email=email, password=password)
    async with uow:
        user_created = await uow.user.create(user_in=user_in)
        await uow.commit()
        user_get = await uow.user.get(id=user_created["id"])
    assert user_created
    assert user_get["email"] == user_created["email"]
