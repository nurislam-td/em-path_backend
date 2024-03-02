from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Response, status
from pydantic import EmailStr

from schemas.token import JWTPayload, TokenOut
from schemas.user import UserCreate, UserDTO, UserResetPassword, UserUpdate
from schemas.verify_code import VerifyOut, VerifyCodeCheck
from service import user, email
from .dependencies import (
    UOWDep,
    get_current_user,
    validate_auth_data,
    validate_refresh_token,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    uow: UOWDep,
) -> UserDTO:
    return await user.create_user(user_data, uow=uow)


@router.post("/users/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    user_data: Annotated[UserDTO, Depends(validate_auth_data)],
    uow: UOWDep,
) -> TokenOut:
    tokens = await user.login(user_data=user_data, uow=uow)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True)
    return tokens


@router.post("/users/email/send_code")
async def send_verify_message(email_in: EmailStr, uow: UOWDep) -> VerifyOut:
    return await email.send_verify_message(email=email_in, uow=uow)


@router.post("/users/email/verify")
async def verify_code(code: VerifyCodeCheck, uow: UOWDep) -> int:
    await email.check_code(code, uow=uow)
    return status.HTTP_200_OK


@router.get("/users/me")
async def get_me(user_data: UserDTO = Depends(get_current_user)) -> UserDTO:
    return user_data


@router.post("/users/token/refresh")
async def refresh_token(
    jwt_payload: Annotated[JWTPayload, Depends(validate_refresh_token)], uow: UOWDep
) -> TokenOut:
    return await user.refresh_tokens(jwt_payload=jwt_payload, uow=uow)


@router.patch("/users/reset_password")
async def reset_password(
    update_data: UserResetPassword,
    uow: UOWDep,
) -> UserDTO:
    return await user.reset_password(update_data=update_data, uow=uow)


@router.patch("/users")
async def update_user(
    update_data: UserUpdate,
    uow: UOWDep,
    user_data: UserDTO = Depends(get_current_user),
) -> UserDTO:
    return await user.update_user(
        user_id=user_data.id, update_data=update_data, uow=uow
    )


@router.delete("/users/{user_id}")
async def delete_user(user_id: UUID, uow: UOWDep):
    await user.delete_user(user_id=user_id, uow=uow)


@router.get("/users/")
async def get_users(uow: UOWDep) -> list[UserDTO]:
    return await user.get_all(uow=uow)
