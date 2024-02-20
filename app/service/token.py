from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
import jwt
from models.auth import RefreshToken
from config.settings import settings
from schemas.token import JWTData, RefreshTokenCreate
from crud.crud_token import token


def encode_jwt(
    payload: dict,
    expire_minutes: int,
    key: str,
    algorithm=settings.auth_config.jwt_alg,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
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
):
    decoded = jwt.decode(
        jwt=token,
        key=key,
        algorithms=[algorithm],
    )
    return decoded


def generate_tokens(
    jwt_data: JWTData,
):
    payload = jsonable_encoder(jwt_data.model_dump())
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


async def saveToken(user_id, refresh_token, session) -> RefreshToken:
    refresh_token_obj = await token.get_by_user_id(db=session, user_id=user_id)
    if refresh_token_obj:
        return await token.update(
            db=session,
            db_obj=refresh_token_obj,
            obj_in={"refresh_token": refresh_token},
        )
    return await token.create(
        db=session, obj_in={"user_id": user_id, "refresh_token": refresh_token}
    )


def validate_refresh_token(token: str):
    try:
        payload = decode_jwt(
            token=token, key=settings.auth_config.refresh_public_path.read_text()
        )
        return payload
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"invalid token error {e}"
        )


def validate_access_token(token: str):
    try:
        payload = decode_jwt(
            token=token, key=settings.auth_config.access_public_path.read_text()
        )
        return payload
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"invalid token error {e}"
        )
