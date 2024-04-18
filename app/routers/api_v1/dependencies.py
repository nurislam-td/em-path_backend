from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)
from pydantic import ValidationError

from app.core.database import IUnitOfWork, UnitOfWork
from app.core.exceptions import IncorrectCredentialsExceptions, InvalidToken
from app.core.settings import settings
from app.schemas.token import JWTPayload
from app.schemas.user import UserDTO, UserLogin
from app.service import secure
from app.service.token import decode_jwt


def get_uow() -> IUnitOfWork:
    return UnitOfWork()


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api_v1/auth/login",
)


async def validate_auth_data(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    uow: IUnitOfWork = Depends(get_uow),
) -> UserDTO:
    try:
        user_credentials = UserLogin.model_validate(form_data)
    except ValidationError as e:
        raise RequestValidationError(e.errors())
    async with uow:
        user_dict = await uow.user.get_by_email(user_credentials.email)
        if not user_dict:
            raise IncorrectCredentialsExceptions
        if not secure.verify_password(user_credentials.password, user_dict["password"]):
            raise IncorrectCredentialsExceptions
        return UserDTO(**user_dict)


def validate_refresh_token(refresh_token: str) -> JWTPayload:
    try:
        payload = decode_jwt(
            token=refresh_token,
            key=settings.auth_config.refresh_public_path.read_text(),
        )
        return JWTPayload.model_validate(payload)

    except InvalidSignatureError:
        raise InvalidToken

    except ExpiredSignatureError:
        raise InvalidToken

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"invalid token error {e}"
        )


def validate_access_token(access_token: str) -> JWTPayload:
    try:
        payload = decode_jwt(
            token=access_token, key=settings.auth_config.access_public_path.read_text()
        )
        return JWTPayload.model_validate(payload)

    except InvalidSignatureError:
        raise InvalidToken

    except ExpiredSignatureError:
        raise InvalidToken

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"invalid token error {e}"
        )


def get_token_payload(token: str = Depends(oauth2_scheme)) -> JWTPayload:
    return validate_access_token(access_token=token)


async def get_current_user(
    payload: JWTPayload = Depends(get_token_payload),
    uow: IUnitOfWork = Depends(get_uow),
) -> UserDTO:
    async with uow:
        user_dict = await uow.user.get(id=payload.sub)
        return UserDTO.model_validate(user_dict)
