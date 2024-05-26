from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi.encoders import jsonable_encoder

from app.core.settings import settings
from app.schemas.token import JWTPayload, TokenOut
from app.service.interfaces.unit_of_work import IUnitOfWork


def encode_jwt(
    payload: dict,
    expire_minutes: int,
    key: str,
    algorithm=settings.auth_config.jwt_alg,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(payload=to_encode, key=key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    key: str,
    algorithm=settings.auth_config.jwt_alg,
) -> dict[str, Any]:
    decoded = jwt.decode(
        jwt=token,
        key=key,
        algorithms=[algorithm],
    )
    return decoded


def generate_tokens(
    jwt_payload: JWTPayload,
) -> tuple[str, str]:
    payload = jsonable_encoder(jwt_payload.model_dump())
    access_token = encode_jwt(
        payload=payload,
        expire_minutes=settings.auth_config.access_token_expire,
        key=settings.auth_config.access_private_path.read_text(),
    )
    refresh_token = encode_jwt(
        payload=payload,
        expire_minutes=settings.auth_config.refresh_token_expire,
        key=settings.auth_config.refresh_private_path.read_text(),
    )
    return access_token, refresh_token


async def get_tokens(payload: dict[str, Any], uow: IUnitOfWork):
    jwt_data = JWTPayload(sub=payload["sub"], email=payload["email"])
    access_token, refresh_token = generate_tokens(jwt_payload=jwt_data)
    async with uow:
        await uow.token.save_token(jwt_data.sub, refresh_token)
        await uow.commit()
        return TokenOut(access_token=access_token, refresh_token=refresh_token)
