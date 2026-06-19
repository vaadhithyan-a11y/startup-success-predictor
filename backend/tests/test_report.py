import pytest
import os


class TestReportService:
    def test_build_summary(self):
        from app.services.report_service import _build_summary_from_predictions
        summary = _build_summary_from_predictions(
            "TestCo", "Tech",
            {"success_probability": 75.0},
            {"growth_1y": 500000, "growth_3y": 1500000, "growth_5y": 3000000},
            {"financial_risk": 25, "operational_risk": 40, "market_risk": 35, "team_risk": 20, "risk_score": 30},
        )
        assert "executive_summary" in summary
        assert len(summary["strengths"]) > 0
        assert "recommendation" in summary
        assert summary["recommendation"] == "Strong Buy"

    def test_low_success_recommendation(self):
        from app.services.report_service import _build_summary_from_predictions
        summary = _build_summary_from_predictions(
            "TestCo", "Tech",
            {"success_probability": 20.0},
            {"growth_1y": -1000, "growth_3y": -3000, "growth_5y": -5000},
            {"financial_risk": 80, "operational_risk": 70, "market_risk": 75, "team_risk": 65, "risk_score": 72.5},
        )
        assert summary["recommendation"] == "Sell"

    def test_generate_pdf(self):
        from app.services.report_service import _generate_pdf
        summary = {
            "executive_summary": "Test summary.",
            "strengths": ["Good team"],
            "weaknesses": ["High burn"],
            "risk_analysis": {"financial": 30, "operational": 40, "market": 50, "team": 20},
            "growth_potential": {"year_1": 100000, "year_3": 300000, "year_5": 500000},
            "recommendation": "Buy",
        }
        path = _generate_pdf("TestStartup", summary)
        assert os.path.exists(path)
        assert path.endswith(".pdf")
        os.remove(path)


@pytest.mark.anyio
async def test_generate_report_endpoint(client):
    await client.post("/auth/register", json={
        "email": "report@example.com", "password": "testpass123", "role": "founder",
    })
    login = await client.post("/auth/login", json={"email": "report@example.com", "password": "testpass123"})
    token = login.json()["access_token"]

    response = await client.post("/report/generate", json={
        "startup_id": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "pdf_url" in data
    assert "summary" in data
    assert "recommendation" in data["summary"]
