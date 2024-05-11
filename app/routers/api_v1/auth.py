from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import EmailStr

from app.interfaces.unit_of_work import IUnitOfWork
from app.schemas.token import JWTPayload, TokenOut
from app.schemas.user import UserDTO, UserResetPassword
from app.schemas.verify_code import VerifyCodeCheck
from app.service import mail_send, user

from ...interfaces.task_manager import ITaskManager
from .dependencies import (
    get_task_manager,
    get_uow,
    validate_auth_data,
    validate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    user_data: Annotated[UserDTO, Depends(validate_auth_data)],
    uow: IUnitOfWork = Depends(get_uow),
) -> TokenOut:
    tokens = await user.login(user_data=user_data, uow=uow)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True)
    return tokens


@router.post("/email", status_code=status.HTTP_202_ACCEPTED)
async def send_verify_message(
    email_in: EmailStr, task_manager: ITaskManager = Depends(get_task_manager)
) -> dict[str, str]:
    task_manager.send_verify_message(email_in=email_in)
    return {"status": "202", "message": "mail has been sent"}


@router.post("/email/code", status_code=status.HTTP_200_OK)
async def verify_code(
    code: VerifyCodeCheck,
    uow: IUnitOfWork = Depends(get_uow),
    task_manager: ITaskManager = Depends(get_task_manager),
) -> bool:
    await mail_send.check_code(code, uow=uow, task_manager=task_manager)
    return True


@router.post("/token/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_token(
    response: Response,
    jwt_payload: JWTPayload = Depends(validate_refresh_token),
    uow: IUnitOfWork = Depends(get_uow),
) -> TokenOut:
    tokens = await user.refresh_tokens(jwt_payload=jwt_payload, uow=uow)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True)
    return tokens


@router.patch("/password", status_code=status.HTTP_200_OK)
async def reset_password(
    update_data: UserResetPassword, uow: IUnitOfWork = Depends(get_uow)
) -> UserDTO:
    return await user.reset_password(update_data=update_data, uow=uow)
