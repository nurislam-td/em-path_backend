from typing import Any
from uuid import UUID

from app.core.database import IUnitOfWork
from app.core.exceptions import UserAlreadyExistsException
from app.schemas.token import JWTPayload, TokenOut
from app.schemas.user import UserCreate, UserDTO, UserResetPassword, UserUpdate
from app.service import token


async def create_user(user_data: UserCreate, uow: IUnitOfWork) -> UserDTO:
    async with uow:
        is_exists = await uow.user.get_by_email(email=user_data.email)
        if is_exists:
            raise UserAlreadyExistsException
        user_dict = await uow.user.create(user_in=user_data)
        await uow.commit()
        return UserDTO(**user_dict)


async def login(user_data: UserDTO, uow: IUnitOfWork) -> TokenOut:
    jwt_data = JWTPayload(sub=user_data.id, email=user_data.email)
    access_token, refresh_token = token.generate_tokens(jwt_payload=jwt_data)
    async with uow:
        await uow.token.saveToken(jwt_data.sub, refresh_token)
        await uow.commit()
        return TokenOut(access_token=access_token, refresh_token=refresh_token)


async def refresh_tokens(jwt_payload: JWTPayload, uow: IUnitOfWork) -> TokenOut:
    access_token, refresh_token = token.generate_tokens(jwt_payload=jwt_payload)
    async with uow:
        await uow.token.saveToken(jwt_payload.sub, refresh_token)
        await uow.commit()
        return TokenOut(access_token=access_token, refresh_token=refresh_token)


async def reset_password(update_data: UserResetPassword, uow: IUnitOfWork) -> UserDTO:
    async with uow:
        user_dict: dict[str, Any] = await uow.user.get_by_email(email=update_data.email)
        updated_user = await uow.user.reset_password(
            user_in=update_data, user_id=user_dict.get("id")
        )
        await uow.commit()
        return UserDTO.model_validate(updated_user)


async def update_user(
    user_id: UUID, update_data: UserUpdate, uow: IUnitOfWork
) -> UserDTO:
    async with uow:
        updated_user = await uow.user.update_one(
            update_data.model_dump(exclude_unset=True), id=user_id
        )
        await uow.commit()
        return UserDTO.model_validate(updated_user)


async def delete_user(user_id: UUID, uow: IUnitOfWork):
    async with uow:
        await uow.user.delete(filters={"id": user_id})
        await uow.commit()


async def get_all(uow: IUnitOfWork) -> list[UserDTO]:
    async with uow:
        users_list = await uow.user.get_all()
        return [UserDTO.model_validate(user_dict) for user_dict in users_list]
