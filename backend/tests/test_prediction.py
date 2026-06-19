import pytest


@pytest.mark.anyio
async def test_predict_success(client):
    await client.post("/auth/register", json={
        "email": "pred@example.com", "password": "testpass123", "role": "founder",
    })
    login = await client.post("/auth/login", json={"email": "pred@example.com", "password": "testpass123"})
    token = login.json()["access_token"]

    response = await client.post("/predict/success", json={
        "industry": "Tech",
        "revenue": 5000000,
        "employees": 100,
        "founder_experience": 10,
        "funding_raised": 10000000,
        "market_size": 500000000,
        "customer_growth": 0.3,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["success_probability"] <= 100
    assert "model_version" in data


@pytest.mark.anyio
async def test_predict_growth(client):
    await client.post("/auth/register", json={
        "email": "growth@example.com", "password": "testpass123", "role": "founder",
    })
    login = await client.post("/auth/login", json={"email": "growth@example.com", "password": "testpass123"})
    token = login.json()["access_token"]

    response = await client.post("/predict/growth", json={
        "revenue": 5000000,
        "employees": 100,
        "funding_raised": 10000000,
        "market_size": 500000000,
        "growth_rate": 0.3,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "growth_1y" in data
    assert "growth_3y" in data
    assert "growth_5y" in data
    assert data["growth_1y"] >= 0


@pytest.mark.anyio
async def test_predict_risk(client):
    await client.post("/auth/register", json={
        "email": "risk@example.com", "password": "testpass123", "role": "founder",
    })
    login = await client.post("/auth/login", json={"email": "risk@example.com", "password": "testpass123"})
    token = login.json()["access_token"]

    response = await client.post("/predict/risk", json={
        "industry": "Tech",
        "revenue": 5000000,
        "employees": 100,
        "founder_experience": 10,
        "funding_raised": 10000000,
        "market_size": 500000000,
        "growth_rate": 0.3,
        "burn_rate": 200000,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "financial_risk" in data
    assert "operational_risk" in data
    assert "market_risk" in data
    assert "team_risk" in data
    assert "risk_score" in data
