import pytest


@pytest.mark.anyio
async def test_register(client):
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "role": "founder",
        "full_name": "Test Founder",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user_id"] > 0


@pytest.mark.anyio
async def test_register_duplicate(client):
    await client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "testpass123",
        "role": "founder",
    })
    response = await client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "testpass123",
        "role": "founder",
    })
    assert response.status_code == 400


@pytest.mark.anyio
async def test_login(client):
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "testpass123",
        "role": "founder",
    })
    response = await client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "testpass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.anyio
async def test_login_invalid(client):
    response = await client.post("/auth/login", json={
        "email": "nonexist@example.com",
        "password": "wrong",
    })
    assert response.status_code == 401
