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
