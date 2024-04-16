import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "nickname, email, password, status_code",
    [
        ("maltipu", "maltipu@email.com", "Gavgavgav01@", 201),
        ("gorelic", "gorelic@email.com", "Gavgavgav02@", 201),
        ("gorelicsandor", "gorelic@email.com", "Gavgavgav02@", 409),
        ("gorelicsandor", "stanin@email.com", "gavgavgav02@", 422),
        ("gorelicsandor", "stanin@email.com", "gavgavgav@", 422),
        ("gorelicsandor", "stanin@email.com", "Gavgavgav@", 422),
        ("gorelicsandor", "stanin@email.com", "gavgavgav", 422),
        ("gorelicsandor", "stanin@email.com", "gavgavgav02", 422),
        ("gorelicsandor", "stanin@email.com", "Gavgavgav02", 422),
    ],
)
async def test_register_user(nickname, email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/api_v1/auth/users",
        json={
            "nickname": nickname,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == status_code


async def test_update_user(auth_ac: AsyncClient):
    response = await auth_ac.patch(
        "/api_v1/auth/users",
        json={
            "email": "user@example.com",
            "nickname": "Malus",
            "sex": "male",
            "name": "IamBatman",
        },
    )
    assert response.status_code == 200
    assert response.json()["nickname"] == "Malus"


@pytest.mark.parametrize(
    "email,password,status_code",
    [
        ("user@example.com", "String03@", 200),
        ("userus@example.com", "String03@", 200),
        ("incorrect@example.com", "String03@", 400),
        ("user@example.com", "String03#", 400),
    ],
)
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/api_v1/auth/users/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == status_code


async def test_get_current_user(auth_ac: AsyncClient):
    response = await auth_ac.get("/api_v1/auth/users/me")
    assert response.status_code == 200


async def test_refresh_token(auth_ac: AsyncClient):
    assert (refresh_token := auth_ac.cookies["refresh_token"])
    response = await auth_ac.post(
        "/api_v1/auth/users/token/refresh-token",
        params={"refresh_token": refresh_token},
    )
    assert response.status_code == 200


async def test_reset_password(ac: AsyncClient):
    response = await ac.patch(
        "/api_v1/auth/users/password",
        json={"email": "user@example.com", "password": "SomeNewPassword03@"},
    )
    assert response.status_code == 200


async def test_user_delete(ac: AsyncClient):
    response = await ac.delete(
        f"/api_v1/auth/users/{'be067225-3570-4673-87f7-d65f6be7b1c1'}",
    )
    assert response.status_code == 200