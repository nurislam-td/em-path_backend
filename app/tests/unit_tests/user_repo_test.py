from uuid import UUID

from app.schemas.user import UserCreate, UserDTO, UserResetPassword
from app.service.abstract.unit_of_work import UnitOfWork


async def test_add_and_get_user_with_pydantic_model(uow: UnitOfWork):
    user_in = UserCreate(
        nickname="melaton", email="coolest2@example.com", password="String03@"
    )
    async with uow:
        assert not (await uow.user.get_by_email(email=user_in.email))
        user_created: UserDTO = await uow.user.create(user_in=user_in)
        assert user_created
        assert isinstance(user_created, UserDTO)
        await uow.commit()
        user_get: UserDTO = await uow.user.get(pk=user_created.id)
        assert isinstance(user_get, UserDTO)
    assert user_get.email == user_created.email


async def test_get_user_by_email(uow: UnitOfWork):
    email = "user@example.com"
    async with uow:
        user_dto: UserDTO = await uow.user.get_by_email(email=email)
        assert user_dto
        assert isinstance(user_dto, UserDTO)
        assert user_dto.email == email


async def test_user_not_exists(uow: UnitOfWork):
    email = "some_random_fake@mail.com"
    async with uow:
        user_dto: None = await uow.user.get_by_email(email=email)
    assert user_dto is None


async def test_user_update(uow: UnitOfWork):
    user_before = dict(
        nickname="string",
        email="userus@example.com",
        id=UUID("32ffa9be-e75e-4ebe-83d7-8d400c6c3bc7"),
        password="$2b$12$pBXO3Qb8Q708eGJV3qyDCOMTwtK8I/2AI4xHzg7SsB8KEnPooWAly",
        gender="other",
        name=None,
        lastname=None,
        patronymic=None,
        date_birth=None,
        image=None,
    )
    user_in = dict(
        name="Mark",
        lastname="Avreli",
    )
    async with uow:
        updated_user: UserDTO = await uow.user.update_one(
            values=user_in,
            pk=user_before["id"],
        )
        assert isinstance(updated_user, UserDTO)
        await uow.commit()
        user_data: UserDTO = await uow.user.get(pk=user_before["id"])
        assert isinstance(user_data, UserDTO)
        assert user_data == updated_user
        assert user_before != updated_user.model_dump()


async def test_reset_password(uow: UnitOfWork):
    user_in = UserResetPassword(email="userus@example.com", password="SomePassHard98$")
    user_id = UUID("32ffa9be-e75e-4ebe-83d7-8d400c6c3bc7")
    password_before = "$2b$12$pBXO3Qb8Q708eGJV3qyDCOMTwtK8I/2AI4xHzg7SsB8KEnPooWAly"
    async with uow:
        user_dto: UserDTO = await uow.user.reset_password(
            user_in=user_in, user_id=user_id
        )
        assert isinstance(user_dto, UserDTO)
        assert user_dto.password != password_before


async def test_user_delete(uow: UnitOfWork):
    async with uow:
        user_id = UUID("ecc14949-46c2-4f18-b71f-31f27c21797e")
        assert not (await uow.user.delete(dict(id=user_id)))
        assert not (await uow.user.get(pk=user_id))
