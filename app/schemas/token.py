from uuid import UUID

from pydantic import BaseModel


class JWTPayload(BaseModel):
    sub: UUID
    email: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenCreate(BaseModel):
    user_id: str
    refresh_token: str
    expires_at: str


class RefreshTokenUpdate(BaseModel):
    refresh_token: str


class RefreshTokenInDB(BaseModel):
    id: str
    user_id: str
    refresh_token: str
    expires_at: str
    created_at: str
    updated_at: str
