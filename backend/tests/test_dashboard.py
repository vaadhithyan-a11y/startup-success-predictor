import pytest


class TestSimilarityService:
    def test_find_similar(self):
        from app.services.similarity_service import SimilarityService
        svc = SimilarityService()
        results = svc.find_similar(0, n=5)
        assert len(results) <= 5
        for r in results:
            assert "startup_id" in r
            assert "similarity_score" in r
            assert 0 <= r["similarity_score"] <= 1

    def test_find_similar_invalid_id(self):
        from app.services.similarity_service import SimilarityService
        svc = SimilarityService()
        results = svc.find_similar(-1, n=5)
        assert results == []


class TestDashboardService:
    def test_get_dashboard_data(self):
        from app.services.dashboard_service import DashboardService
        svc = DashboardService()
        data = svc.get_dashboard_data()
        assert "rankings" in data
        assert "risk_distribution" in data
        assert "funding_trends" in data
        assert "industry_analysis" in data
        assert len(data["rankings"]) > 0
        assert len(data["funding_trends"]) > 0


@pytest.mark.anyio
async def test_dashboard_endpoint(client):
    await client.post("/auth/register", json={
        "email": "dash@example.com", "password": "testpass123", "role": "founder",
    })
    login = await client.post("/auth/login", json={"email": "dash@example.com", "password": "testpass123"})
    token = login.json()["access_token"]

    response = await client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "rankings" in data


@pytest.mark.anyio
async def test_similar_endpoint(client):
    await client.post("/auth/register", json={
        "email": "sim@example.com", "password": "testpass123", "role": "founder",
    })
    login = await client.post("/auth/login", json={"email": "sim@example.com", "password": "testpass123"})
    token = login.json()["access_token"]

    response = await client.get("/similar?startup_id=0&n=3", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
