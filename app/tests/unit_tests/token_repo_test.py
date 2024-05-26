from uuid import UUID

from app.schemas.token import TokenDTO
from app.service.interfaces.unit_of_work import IUnitOfWork


async def test_get_by_user_id(uow: IUnitOfWork):
    user_id = UUID("32ffa9be-e75e-4ebe-83d7-8d400c6c3bc7")
    async with uow:
        token = await uow.token.get_by_user_id(user_id=user_id)
        assert token


async def test_save_token(uow: IUnitOfWork):
    user_id = UUID("7f458c5b-ed99-41f4-b451-a5b220a60a1c")
    async with uow:
        assert await uow.token.get_by_user_id(user_id=user_id) is None
        refresh_token_dto: TokenDTO = await uow.token.save_token(
            user_id=user_id, refresh_token="refresh_token"
        )
        await uow.commit()
        assert await uow.token.get_by_user_id(user_id=user_id) == refresh_token_dto
        refresh_token_updated = await uow.token.save_token(
            user_id=user_id, refresh_token="refresh_token_updated"
        )
        await uow.commit()
        assert await uow.token.get_by_user_id(user_id=user_id) == refresh_token_updated
