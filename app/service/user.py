from sqlalchemy.ext.asyncio import AsyncSession
from schemas.token import JWTData, TokenOut
from crud.crud_user import user
from schemas.user import UserCreate, AuthUser
from fastapi import HTTPException, status
from service import secure, token


async def validate_auth_data(user_data: AuthUser, session: AsyncSession):
    user_obj = await user.get_by_email(db=session, email=user_data.email)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid email or password"
        )
    if not secure.verify_password(user_data.password, user_obj.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid email or password"
        )
    return user_obj


async def create_user(user_data: UserCreate, session: AsyncSession):
    is_exists = await user.get_by_email(db=session, email=user_data.email)
    if is_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    return await user.create(db=session, obj_in=user_data)


async def login(auth_data: AuthUser, session: AsyncSession):
    user_obj = await validate_auth_data(auth_data, session)
    jwt_data = JWTData(sub=user_obj.user_id, email=user_obj.email)
    access_token, refresh_token = token.generate_tokens(jwt_data=jwt_data)
    await token.saveToken(user_obj.user_id, refresh_token, session)
    return TokenOut(access_token=access_token, refresh_token=refresh_token)


async def refresh_tokens(refresh_token: str, session: AsyncSession):
    payload = token.validate_refresh_token(token=refresh_token)
    jwt_data = JWTData(sub=payload["sub"], email=payload["email"])
    access_token, refresh_token = token.generate_tokens(jwt_data=jwt_data)
    await token.saveToken(payload["sub"], refresh_token, session)
    return TokenOut(access_token=access_token, refresh_token=refresh_token)
