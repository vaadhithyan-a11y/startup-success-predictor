import pytest


@pytest.mark.anyio
async def test_create_startup(client):
    reg = await client.post("/auth/register", json={
        "email": "founder@example.com",
        "password": "testpass123",
        "role": "founder",
        "full_name": "Founder",
    })
    user_id = reg.json()["user_id"]

    login = await client.post("/auth/login", json={
        "email": "founder@example.com",
        "password": "testpass123",
    })
    token = login.json()["access_token"]

    response = await client.post("/startup", json={
        "founder_id": user_id,
        "name": "Test Startup",
        "industry": "Tech",
        "location": "San Francisco",
        "founding_year": 2020,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["startup_id"] > 0


@pytest.mark.anyio
async def test_get_startup_not_found(client):
    await client.post("/auth/register", json={
        "email": "founder2@example.com",
        "password": "testpass123",
        "role": "founder",
    })
    login = await client.post("/auth/login", json={
        "email": "founder2@example.com",
        "password": "testpass123",
    })
    token = login.json()["access_token"]

    response = await client.get("/startup/9999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_startup_found(client):
    await client.post("/auth/register", json={
        "email": "founder3@example.com", "password": "testpass123", "role": "founder", "full_name": "F3",
    })
    login = await client.post("/auth/login", json={"email": "founder3@example.com", "password": "testpass123"})
    token = login.json()["access_token"]
    create = await client.post("/startup", json={
        "founder_id": 1, "name": "GetTest", "industry": "BioTech", "location": "Boston",
    }, headers={"Authorization": f"Bearer {token}"})
    sid = create.json()["startup_id"]

    response = await client.get(f"/startup/{sid}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sid
    assert data["data"]["name"] == "GetTest"
    assert data["data"]["industry"] == "BioTech"
