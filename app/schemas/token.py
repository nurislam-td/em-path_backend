from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TokenDTO(BaseModel):
    id: UUID
    user_id: UUID
    refresh_token: str
    created_at: datetime
    updated_at: datetime


class JWTPayload(BaseModel):
    sub: UUID
    email: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
