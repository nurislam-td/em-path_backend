from typing import Type

import pytest
from pydantic import BaseModel, EmailStr, ValidationError

from app.schemas.user import UserCreate, UserLogin, UserResetPassword, UserUpdate


def pytest_generate_tests(metafunc):
    if "schema" in metafunc.fixturenames:
        metafunc.parametrize(
            "schema", [UserCreate, UserResetPassword, UserUpdate, UserLogin]
        )
    if "pass_schema" in metafunc.fixturenames:
        metafunc.parametrize("pass_schema", [UserCreate, UserResetPassword, UserLogin])


def test_good_schema(schema: Type[BaseModel]):
    assert schema(
        email="good@example.com", password="GoodPassword03$", nickname="SomeNick"
    )


@pytest.mark.parametrize("email", ["bad_mail.com", "bad@email"])
def test_bad_email_schema(email: EmailStr, schema: Type[BaseModel]):
    with pytest.raises(ValidationError):
        schema(email=email, password="GoodPassword03$", nickname="SomeNick")


@pytest.mark.parametrize(
    "password", ["bad_pass", "bad@pass", "BadPassword03", "BadPassword@"]
)
def test_bad_password_schema(password: str, pass_schema: Type[BaseModel]):
    with pytest.raises(ValidationError):
        pass_schema(email="mail@mail.com", password=password, nickname="SomeNick")


def test_fail_empty_update_schema():
    with pytest.raises(ValidationError):
        UserUpdate()
