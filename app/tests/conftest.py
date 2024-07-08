import json
import os
from datetime import datetime
from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

from app.service.abstract.task_manager import ITaskManager

# TODO refactor this import
os.environ["MODE"] = "TEST"
from app.adapters.unit_of_work import SQLAlchemyUnitOfWork
from app.common.database import async_engine, async_session_maker
from app.common.settings import settings
from app.main import app as fastapi_app
from app.models.auth import RefreshToken, User, VerifyCode
from app.models.base import Base


@pytest.fixture(scope="session", autouse=True)
async def prepare_database() -> None:
    assert settings.MODE == "TEST"
    assert str(async_engine.url).endswith("test", -4)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", encoding="utf-8") as file:
            return json.load(file)

    users = open_mock_json("users")
    for user in users:
        user["password"] = bytes(user["password"], "utf-8")

    tokens = open_mock_json("tokens")
    for token in tokens:
        token["created_at"] = datetime.now()
        token["updated_at"] = datetime.now()

    verify_codes = open_mock_json("verify_codes")
    for verify_code in verify_codes:
        verify_code["created_at"] = datetime.now()

    async with async_session_maker() as session:
        add_users = insert(User).values(users)
        add_tokens = insert(RefreshToken).values(tokens)
        add_verify_codes = insert(VerifyCode).values(verify_codes)

        await session.execute(add_users)
        await session.execute(add_tokens)
        await session.execute(add_verify_codes)

        await session.commit()


# @pytest.fixture(scope="session")
# def event_loop(request):
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()
# TODO watch this event loop


@pytest.fixture(scope="function")
async def ac() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
async def auth_ac() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as auth_ac:
        response = await auth_ac.post(
            "/api/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "String03@",
            },
        )
        response_data = response.json()
        assert response_data["refresh_token"]
        assert (access_token := response_data["access_token"])
        auth_ac.headers["Authorization"] = f"Bearer {access_token}"
        yield auth_ac


@pytest.fixture(scope="function")
async def uow() -> AsyncGenerator[SQLAlchemyUnitOfWork, Any]:
    yield SQLAlchemyUnitOfWork(async_session_maker)


# TODO add "celery" task test
# TODO optimize mock json files
# TODO learn test mocking


class TestTaskManager:
    @staticmethod
    def send_verify_message(email_in: str):
        return bool(email_in)

    @staticmethod
    def deactivate_verify_code(email_in: str):
        return bool(email_in)

    @staticmethod
    def clean_verify_code_table():
        return True


@pytest.fixture
def task_manager() -> ITaskManager:
    return TestTaskManager()
