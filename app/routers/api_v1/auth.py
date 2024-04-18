from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from pydantic import EmailStr

from app.core.database import IUnitOfWork
from app.schemas.token import JWTPayload, TokenOut
from app.schemas.user import UserCreate, UserDTO, UserResetPassword, UserUpdate
from app.schemas.verify_code import VerifyCodeCheck
from app.service import email, user

from .dependencies import (
    get_current_user,
    get_uow,
    validate_auth_data,
    validate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, uow: IUnitOfWork = Depends(get_uow)
) -> TokenOut:
    user_data = await user.create_user(user_data, uow=uow)
    tokens = await user.login(user_data=user_data, uow=uow)
    return tokens


@router.post("/users/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    user_data: Annotated[UserDTO, Depends(validate_auth_data)],
    uow: IUnitOfWork = Depends(get_uow),
) -> TokenOut:
    tokens = await user.login(user_data=user_data, uow=uow)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True)
    return tokens


@router.post("/users/email", status_code=status.HTTP_200_OK)
async def send_verify_message(
    background_tasks: BackgroundTasks,
    email_in: EmailStr,
    uow: IUnitOfWork = Depends(get_uow),
) -> dict[str, str]:
    background_tasks.add_task(email.send_verify_message, email_in, uow)
    return {"status": "202", "message": "mail has been sended"}


@router.post("/users/email/code", status_code=status.HTTP_200_OK)
async def verify_code(
    code: VerifyCodeCheck, uow: IUnitOfWork = Depends(get_uow)
) -> bool:
    await email.check_code(code, uow=uow)
    return True


@router.get("/users/me", status_code=status.HTTP_200_OK)
async def get_me(user_data: UserDTO = Depends(get_current_user)) -> UserDTO:
    return user_data


@router.post("/users/token/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_token(
    response: Response,
    jwt_payload: JWTPayload = Depends(validate_refresh_token),
    uow: IUnitOfWork = Depends(get_uow),
) -> TokenOut:
    tokens = await user.refresh_tokens(jwt_payload=jwt_payload, uow=uow)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True)
    return tokens


@router.patch("/users/password", status_code=status.HTTP_200_OK)
async def reset_password(
    update_data: UserResetPassword, uow: IUnitOfWork = Depends(get_uow)
) -> UserDTO:
    return await user.reset_password(update_data=update_data, uow=uow)


@router.patch("/users", status_code=status.HTTP_200_OK)
async def update_user(
    update_data: UserUpdate,
    uow: IUnitOfWork = Depends(get_uow),
    user_data: UserDTO = Depends(get_current_user),
) -> UserDTO:
    return await user.update_user(
        user_id=user_data.id, update_data=update_data, uow=uow
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: UUID, uow: IUnitOfWork = Depends(get_uow)) -> None:
    await user.delete_user(user_id=user_id, uow=uow)


@router.get("/users", status_code=status.HTTP_200_OK)
async def get_users(uow: IUnitOfWork = Depends(get_uow)) -> list[UserDTO]:
    return await user.get_all(uow=uow)
