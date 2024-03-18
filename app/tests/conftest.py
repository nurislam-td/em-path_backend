import asyncio
import json

import pytest
from sqlalchemy import insert

from app.core.database import async_session_maker, engine
from app.core.settings import settings
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


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
