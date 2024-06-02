from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)
from pydantic import EmailStr

from app.common.exceptions import (
    IncorrectCredentialsExceptions,
    InvalidToken,
    UserAlreadyExistsException,
    UserNotExistsException,
)
from app.common.settings import settings
from app.repo.file_client import S3FileClient
from app.repo.unit_of_work import SQLAlchemyUnitOfWork
from app.schemas.token import JWTPayload
from app.schemas.user import UserDTO, UserLogin
from app.service import secure
from app.service.abstract.file_client import FileClient
from app.service.abstract.task_manager import ITaskManager
from app.service.abstract.unit_of_work import UnitOfWork
from app.service.token import decode_jwt
from app.tasks.tasks import CeleryTaskManager


def get_uow() -> UnitOfWork:
    return SQLAlchemyUnitOfWork()


def get_task_manager() -> ITaskManager:
    return CeleryTaskManager()


def get_file_client() -> FileClient:
    return S3FileClient(
        access_key=settings.s3.access_key,
        secret_key=settings.s3.secret_key,
        bucket_name=settings.s3.private_bucket_name,
        endpoint_url=settings.s3.endpoint_url,
    )


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api_v1/auth/login",
)

http_bearer = HTTPBearer(auto_error=False)


async def validate_auth_data(
    user_credentials: UserLogin,
    uow: UnitOfWork = Depends(get_uow),
) -> UserDTO:
    async with uow:
        user_dto: UserDTO = await uow.user.get_by_email(user_credentials.email)
        if not user_dto:
            raise IncorrectCredentialsExceptions
        if not secure.verify_password(user_credentials.password, user_dto.password):
            raise IncorrectCredentialsExceptions
        return user_dto


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


def get_token_payload(
    http_auth: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> JWTPayload:
    if not http_auth:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = http_auth.credentials
    return validate_access_token(access_token=token)


async def check_email_exists(
    email_in: EmailStr, uow: UnitOfWork = Depends(get_uow)
) -> EmailStr:
    async with uow:
        user_dto: UserDTO = await uow.user.get_by_email(email_in)
        if user_dto:
            raise UserAlreadyExistsException
    return email_in


async def get_current_user(
    payload: JWTPayload = Depends(get_token_payload),
    uow: UnitOfWork = Depends(get_uow),
) -> UserDTO:
    async with uow:
        user_dto: UserDTO = await uow.user.get(pk=payload.sub)
        if user_dto:
            return user_dto
        raise UserNotExistsException
