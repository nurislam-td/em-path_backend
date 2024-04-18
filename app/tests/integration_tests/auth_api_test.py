import pytest
from httpx import AsyncClient

url = "/api_v1/auth"


@pytest.mark.parametrize(
    "email,password,status_code",
    [
        ("user@example.com", "String03@", 200),
        ("userus@example.com", "String03@", 200),
        ("userus@example.com", "String03", 422),
        ("userus2example.com", "String03@", 422),
        ("userus2example.com", "String03", 422),
        ("incorrect@example.com", "String03@", 400),
        ("user@example.com", "String03#", 400),
    ],
)
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        f"{url}/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == status_code


async def test_refresh_token(auth_ac: AsyncClient):
    assert (refresh_token := auth_ac.cookies["refresh_token"])
    response = await auth_ac.post(
        f"{url}/token/refresh-token",
        params={"refresh_token": refresh_token},
    )
    assert response.status_code == 200


async def test_reset_password(ac: AsyncClient):
    response = await ac.patch(
        f"{url}/password",
        json={"email": "user@example.com", "password": "SomeNewPassword03@"},
    )
    assert response.status_code == 200
