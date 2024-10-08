from uuid import UUID

from app.common.exceptions import UserAlreadyExistsException, UserNotExistsException
from app.common.settings import settings
from app.schemas.token import JWTPayload, TokenOut
from app.schemas.user import UserCreate, UserDTO, UserResetPassword, UserUpdate
from app.service import token
from app.service.abstract.file_client import FileClient
from app.service.abstract.unit_of_work import UnitOfWork


async def create_user(user_data: UserCreate, uow: UnitOfWork) -> UserDTO:
    async with uow:
        if await uow.user.get_by_email(email=user_data.email):
            raise UserAlreadyExistsException
        user_dto: UserDTO = await uow.user.create(user_in=user_data)
        await uow.commit()
        return user_dto


async def login(user_data: UserDTO, uow: UnitOfWork) -> TokenOut:
    jwt_data = JWTPayload(sub=user_data.id, email=user_data.email)
    access_token, refresh_token = token.generate_tokens(jwt_payload=jwt_data)
    async with uow:
        await uow.token.save_token(jwt_data.sub, refresh_token)
        await uow.commit()
        return TokenOut(access_token=access_token, refresh_token=refresh_token)


async def refresh_tokens(jwt_payload: JWTPayload, uow: UnitOfWork) -> TokenOut:
    access_token, refresh_token = token.generate_tokens(jwt_payload=jwt_payload)
    async with uow:
        await uow.token.save_token(jwt_payload.sub, refresh_token)
        await uow.commit()
        return TokenOut(access_token=access_token, refresh_token=refresh_token)


async def reset_password(
    update_data: UserResetPassword, uow: UnitOfWork
) -> UserDTO | None:
    async with uow:
        user_dto: UserDTO | None = await uow.user.get_by_email(email=update_data.email)
        if not user_dto:
            raise UserNotExistsException
        updated_user = await uow.user.reset_password(
            user_in=update_data, user_id=user_dto.id
        )
        await uow.commit()
        return updated_user


async def update_user(
    user_id: UUID,
    update_data: UserUpdate,
    uow: UnitOfWork,
    file_client: FileClient,
) -> UserDTO:
    if update_data.image:
        file_name = "-".join(update_data.image.filename.strip().split(" "))
        file_path = f"avatar/{user_id}/{file_name}"
        image_url = (
            f"{settings.s3.endpoint_url}/{settings.s3.public_bucket_name}/{file_path}"
        )
        await file_client.upload_file(file=update_data.image.file, file_path=file_path)
        update_data.image = image_url
    async with uow:
        updated_user: UserDTO = await uow.user.update_one(
            update_data.model_dump(exclude_unset=True, exclude_none=True), pk=user_id
        )
        await uow.commit()
        return updated_user


async def delete_user(user_id: UUID, uow: UnitOfWork):
    async with uow:
        await uow.user.delete(filters={"id": user_id})
        await uow.commit()


async def get_all(uow: UnitOfWork) -> list[UserDTO] | None:
    async with uow:
        users_list: list[UserDTO] | None = await uow.user.get_all()
        return users_list
