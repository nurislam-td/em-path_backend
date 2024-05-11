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

from app.core.exceptions import (
    IncorrectCredentialsExceptions,
    InvalidToken,
    UserNotExistsException,
)
from app.core.settings import settings
from app.interfaces.task_manager import ITaskManager
from app.interfaces.unit_of_work import IUnitOfWork
from app.repo.unit_of_work import UnitOfWork
from app.schemas.token import JWTPayload
from app.schemas.user import UserDTO, UserLogin
from app.service import secure
from app.service.token import decode_jwt
from app.tasks.tasks import CeleryTaskManager


def get_uow() -> IUnitOfWork:
    return UnitOfWork()


def get_task_manager() -> ITaskManager:
    return CeleryTaskManager()


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api_v1/auth/login",
)
http_bearer = HTTPBearer()


async def validate_auth_data(
    user_credentials: UserLogin,
    uow: IUnitOfWork = Depends(get_uow),
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
    token = http_auth.credentials
    return validate_access_token(access_token=token)


async def get_current_user(
    payload: JWTPayload = Depends(get_token_payload),
    uow: IUnitOfWork = Depends(get_uow),
) -> UserDTO:
    async with uow:
        user_dto: UserDTO = await uow.user.get(pk=payload.sub)
        if user_dto:
            return user_dto
        raise UserNotExistsException
