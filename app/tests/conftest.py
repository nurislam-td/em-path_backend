import asyncio
import json

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

from app.core.database import UnitOfWork, async_session_maker, engine
from app.core.settings import settings
from app.main import app as fastapi_app
from app.models.auth import User
from app.models.base import Base


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", encoding="utf-8") as file:
            return json.load(file)

    users = open_mock_json("users")
    for user in users:
        user["password"] = bytes(user["password"], "utf-8")
    # verify_codes = open_mock_json("verify_codes")

    async with async_session_maker() as session:
        add_users = insert(User).values(users)
        # add_verify_codes = insert(VerifyCode).values(verify_codes)

        await session.execute(add_users)
        # await session.execute(add_verify_codes)

        await session.commit()


# @pytest.fixture(scope="session")
# def event_loop(request):
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def auth_ac():
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/api_v1/auth/users/login",
            data={
                "username": "user@example.com",
                "password": "String03@",
            },
        )
        access_token = response.json()["access_token"]
        assert access_token
        ac.headers["Authorization"] = f"Bearer {access_token}"
        yield ac


@pytest.fixture(scope="function")
async def uow():
    yield UnitOfWork(async_session_maker)
