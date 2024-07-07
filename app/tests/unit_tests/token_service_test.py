from uuid import UUID

import pytest

from app.common.settings import settings
from app.schemas.token import JWTPayload, TokenOut
from app.service import token
from app.service.abstract.unit_of_work import UnitOfWork


@pytest.fixture(scope="function")
async def payload() -> dict:
    return {
        "sub": "ae538ea8-0cc0-4e06-9649-f5fa7c28701b",
        "email": "user@example.com",
    }


async def test_encode_access_token(payload: dict):
    access_token = token.encode_jwt(
        payload=payload,
        expire_minutes=settings.auth_config.access_token_expire,
        key=settings.auth_config.access_private_path.read_text(),
    )
    assert access_token


async def test_encode_refresh_token(payload: dict):
    refresh_token = token.encode_jwt(
        payload=payload,
        expire_minutes=settings.auth_config.refresh_token_expire,
        key=settings.auth_config.refresh_private_path.read_text(),
    )
    assert refresh_token


async def test_generate_tokens(payload: dict):
    tokens = token.generate_tokens(JWTPayload(**payload))
    assert len(tokens) == 2


async def test_get_tokens(uow: UnitOfWork, payload: dict):
    tokens = await token.get_tokens(payload=payload, uow=uow)
    assert isinstance(tokens, TokenOut)
    assert len(tokens.model_dump()) == 2
    async with uow:
        refresh_token_dto = await uow.token.get_by_user_id(UUID(payload["sub"]))
        assert refresh_token_dto is not None, "REFRESH TOKEN NOT EXISTS"
